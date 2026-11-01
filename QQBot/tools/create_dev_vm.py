#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创建开发虚拟机（KVM），把开发面板从生产机上搬过去。

背景（2026-11-01）：
  之前开发实例和生产在同一台机器上共用 /opt/rcbot 与同一套端口，
  互相干扰（改一份配置两个面板都变、dev 非 root 写不进 root 目录、
  插件部署 400）。这个脚本建一台独立虚拟机承载开发环境。

最终方案（2026-11-02 定稿，实测可用）
  ---------------------------------------------------------------
  不用 libvirt 管这个虚拟机，而是 **systemd 直接跑 qemu**。

  原因：libvirt 9.0 在这台宿主上不支持 passt 后端，
  <interface type='user'> 的 <portForward> 也生成不出 qemu 的 hostfwd
  （range/toPort 三种写法都试过，dumpxml 里都被丢掉）。
  而 SLIRP 的 guest 网络本身完全正常（静态地址、网关、sshd 全通），
  只差一个端口转发 —— 直接给 qemu 写 hostfwd 最直接。

  网络：qemu SLIRP（用户态网络，不依赖宿主 dnsmasq）
    · 机内静态地址 10.0.2.15/24，网关 10.0.2.2，DNS 10.0.2.3
      —— 不等 DHCP（用户明确要求）
    · 宿主 hostfwd：
        0.0.0.0:3910  ->  机内 3910   （开发面板，局域网可访问）
        127.0.0.1:2223 -> 机内 22     （SSH，只给本机）
        127.0.0.1:6711 -> 机内 6710   （rcbot HTTP）
    · 不需要任何 iptables DNAT：
      hostfwd 绑的是 0.0.0.0:3910，外部机器访问 192.168.2.200:3910
      时目标就是宿主自己的地址，走 INPUT 链直接命中 qemu 监听。
      （★ 多加一条 DNAT 到 127.0.0.1 反而会让外部连不上：
        外部来源的包目标被改成 loopback，route_localnet=0 时内核丢弃。
        宿主本机走 OUTPUT 链不受影响，所以本机测是 200、别人测超时。）

  外部访问：
    开发面板 http://192.168.2.200:3910
    生产面板 http://192.168.2.200:3900

用法（在宿主机上以 root 执行）：
    python3 tools/create_dev_vm.py
"""
import os
import subprocess
import time

VM_NAME = 'rcbot-dev'
VM_MEM = 4096          # MB
VM_CPUS = 2
VM_DISK = '30G'
VM_MAC = '52:54:00:6b:12:37'

GUEST_IP = '10.0.2.15'
GUEST_GW = '10.0.2.2'
GUEST_DNS = '10.0.2.3'
HOST_IP = '192.168.2.200'

# 宿主端口 -> 机内端口（qemu hostfwd）
#   3910 对外（开发面板）；2223/6711 只绑 127.0.0.1
PORT_FWD = [
    ('0.0.0.0', 3910, 3910),
    ('127.0.0.1', 2223, 22),
    ('127.0.0.1', 6711, 6710),
]

HOST_PUBKEY = '/root/.ssh/rcbot-vm.pub'
BASE_IMG = '/var/lib/libvirt/images/debian12-base.qcow2'
DISK = '/var/lib/libvirt/images/rcbot-dev.qcow2'
SEED_DIR = '/var/lib/libvirt/seed'
SEED_IMG = os.path.join(SEED_DIR, '%s-seed.img' % VM_NAME)
SSH_KEY = '/root/.ssh/rcbot-vm'
FALLBACK_PUB = ('ssh-ed25519 '
                'AAAAC3NzaC1lZDI1NTE5AAAAIP17ZTStk/Lr3AAkwCY1gZxgp2ylDwKfW3+zHar69v/1 '
                'rcbot-vm')


def sh(cmd, check=True):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors='replace')
    out = (p.stdout or '') + (p.stderr or '')
    if check and p.returncode != 0:
        raise RuntimeError('命令失败: %s\n%s' % (cmd, out[-2000:]))
    return p.returncode, out


def need(cmd, what):
    _, o = sh('command -v %s' % cmd, check=False)
    if not o.strip():
        raise SystemExit('缺少 %s（%s）' % (cmd, what))
    return o.strip()


def qemu_args():
    fwd = ','.join('hostfwd=tcp:%s:%d-:%d' % (a, h, g) for a, h, g in PORT_FWD)
    return [
        '/usr/bin/qemu-system-x86_64',
        '-name', '%s,process=%s' % (VM_NAME, VM_NAME),
        '-machine', 'pc,accel=kvm',
        '-cpu', 'host',
        '-m', str(VM_MEM),
        '-smp', str(VM_CPUS),
        '-drive', 'file=%s,format=qcow2,if=virtio,cache=writeback' % DISK,
        '-drive', 'file=%s,format=raw,if=virtio,readonly=on' % SEED_IMG,
        '-netdev', 'user,id=net0,%s' % fwd,
        '-device', 'virtio-net-pci,netdev=net0,mac=%s' % VM_MAC,
        '-display', 'none',
        '-serial', 'file:/var/log/%s-serial.log' % VM_NAME,
        '-vga', 'std',
        '-no-reboot',
    ]


def write_cloud_init(pub):
    """cloud-init：SSH 免密 + 静态地址。

    ★ 网络配置必须放 network-config 文件（cloud-localds --network-config），
      不能放 user-data 的 network: 键 —— cloud-init 22.4.2 的 schema
      不认那种写法，会报 "Invalid cloud-config provided" 并**整段丢弃**，
      结果网卡既没静态地址也没 DHCP（实测踩过）。
    ★ 静态地址，不等 DHCP。
    ★ instance-id 每次都要换，否则 cloud-init 认为已配置过，网络阶段会跳过。
    """
    user_data = """#cloud-config
users:
  - name: rcbot
    groups: sudo
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: true
    ssh_authorized_keys:
      - %s
ssh_pwauth: false
disable_root: true
package_update: false
write_files:
  # 兜底: 万一 network-config 没生效, 这里补一份 networkd 静态配置
  - path: /etc/systemd/network/10-ens3-static.network
    permissions: '0644'
    content: |
      [Match]
      Name=ens3

      [Network]
      Address=%s/24
      Gateway=%s
      DNS=%s
      DNS=223.5.5.5
runcmd:
  - [ systemctl, restart, systemd-networkd ]
  - [ sh, -c, "echo rcbot-vm-ready > /var/log/rcbot-vm-ready" ]
""" % (pub, GUEST_IP, GUEST_GW, GUEST_DNS)

    network_config = """version: 2
ethernets:
  ens3:
    dhcp4: false
    addresses:
      - %s/24
    routes:
      - to: default
        via: %s
    nameservers:
      addresses:
        - %s
        - 223.5.5.5
""" % (GUEST_IP, GUEST_GW, GUEST_DNS)

    os.makedirs(SEED_DIR, exist_ok=True)
    ud = os.path.join(SEED_DIR, 'user-data')
    md = os.path.join(SEED_DIR, 'meta-data')
    nc = os.path.join(SEED_DIR, 'network-config')
    with open(ud, 'w', encoding='utf-8') as f:
        f.write(user_data)
    with open(md, 'w', encoding='utf-8') as f:
        f.write('instance-id: %s-%s\nlocal-hostname: %s\n'
                % (VM_NAME, int(time.time()), VM_NAME))
    with open(nc, 'w', encoding='utf-8') as f:
        f.write(network_config)

    if os.path.exists(SEED_IMG):
        os.remove(SEED_IMG)
    sh('cloud-localds --network-config=%s %s %s %s' % (nc, SEED_IMG, ud, md))
    if not os.path.exists(SEED_IMG):
        raise RuntimeError('cloud-localds 没生成种子镜像')


def write_unit():
    args = ' \\\n  '.join(qemu_args())
    unit = """[Unit]
Description=RainCough 开发实例虚拟机 (%(name)s)
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart=%(args)s
Restart=always
RestartSec=5
TimeoutStopSec=30
KillMode=control-group

[Install]
WantedBy=multi-user.target
""" % {'name': VM_NAME, 'args': args}
    path = '/etc/systemd/system/%s.service' % VM_NAME
    with open(path, 'w', encoding='utf-8') as f:
        f.write(unit)
    return path


def clear_dnat():
    """清掉可能残留的 3910/2223/6711 的 DNAT 规则。

    ★ 为什么不需要 DNAT（踩过这个坑）：
      qemu 的 hostfwd 监听在 **0.0.0.0:3910**，外部机器访问
      192.168.2.200:3910 时，目标 IP 就是宿主自己的地址，
      包走 INPUT 链直接命中 qemu 的监听 —— 本来就能通。

      之前我多写了一条 DNAT：
          -d 192.168.2.200/32 --dport 3910 -j DNAT --to-destination 127.0.0.1:3910
      结果外部来源的包目标被改成 loopback，而内核
      net.ipv4.conf.all.route_localnet=0 → 拒绝路由 → 包被丢弃 →
      外部连不上（宿主本机走 OUTPUT 链不受影响，所以本机测是 200，
      看起来"一切正常"，实际别人都打不开）。

      所以这里只做"清理"，不做"添加"。
    """
    for host, guest, bind in PORT_FWD:
        for chain in ('PREROUTING', 'OUTPUT'):
            sh('iptables -t nat -D %s -d %s/32 -p tcp --dport %d '
               '-j DNAT --to-destination 127.0.0.1:%d 2>/dev/null'
               % (chain, HOST_IP, host, host), check=False)
    sh('netfilter-persistent save >/dev/null 2>&1', check=False)


def main():
    need('qemu-system-x86_64', 'qemu')
    need('qemu-img', 'qemu 工具')
    need('cloud-localds', 'cloud-init 种子')

    if not os.path.exists(BASE_IMG):
        raise SystemExit('缺少基础镜像: %s' % BASE_IMG)
    if not os.path.exists(SSH_KEY):
        raise SystemExit('缺少 SSH 私钥: %s' % SSH_KEY)

    pub = ''
    if os.path.exists(HOST_PUBKEY):
        with open(HOST_PUBKEY, 'r', encoding='utf-8') as f:
            pub = f.read().strip()
    pub = pub or FALLBACK_PUB

    # 1) 磁盘（每次重建，cloud-init 才会重新配置网络）
    sh('systemctl stop %s 2>/dev/null' % VM_NAME, check=False)
    time.sleep(2)
    if os.path.exists(DISK):
        os.remove(DISK)
    sh('qemu-img create -f qcow2 -F qcow2 -b %s %s %s' % (BASE_IMG, DISK, VM_DISK))
    print('磁盘已重建: %s' % DISK)

    # 2) cloud-init
    write_cloud_init(pub)
    print('cloud-init 种子已生成（静态地址 %s，不等 DHCP）' % GUEST_IP)

    # 3) systemd 单元
    path = write_unit()
    sh('systemctl daemon-reload')
    sh('systemctl enable %s' % VM_NAME)
    print('systemd 单元: %s' % path)

    # 4) 启动
    sh('systemctl start %s' % VM_NAME)
    time.sleep(4)
    print('虚拟机: %s' % sh('systemctl is-active %s 2>&1' % VM_NAME).strip())

    # 5) 清理可能残留的 DNAT 规则（见 clear_dnat 的注释）
    clear_dnat()
    print()
    print('端口转发（qemu hostfwd，不需要额外 DNAT）:')
    for a, h, g in PORT_FWD:
        print('   %s:%d  ->  %s:%d' % (a, h, GUEST_IP, g))
    print()
    print('外部访问开发面板: http://%s:3910' % HOST_IP)
    print('外部访问生产面板: http://%s:3900' % HOST_IP)
    print('免密登录虚拟机: ssh -p 2223 -i %s rcbot@127.0.0.1' % SSH_KEY)

    # 6) 等 SSH
    print()
    print('等机内 SSH 就绪...')
    for i in range(40):
        _, o = sh('ssh -p 2223 -i %s -o StrictHostKeyChecking=no '
                  '-o ConnectTimeout=5 -o BatchMode=yes rcbot@127.0.0.1 '
                  '"echo VM_OK" 2>&1' % SSH_KEY, check=False)
        if 'VM_OK' in o:
            print('  SSH 就绪（第 %d 次探测）' % (i + 1))
            break
        time.sleep(5)
    else:
        print('  ! 机内还没通。串口日志: /var/log/%s-serial.log' % VM_NAME)


if __name__ == '__main__':
    main()
