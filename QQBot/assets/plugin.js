(()=>{var gl,Fe,ke,_s,Ss,Tn,Ki,Cn,Wr,_i,Fi,ai,Jr;function bt(e){let t=Object.create(null);for(let i of e.split(","))t[i]=1;return i=>i in t}var pe={},Qi=[],He=()=>{},$i=()=>!1,Ri=e=>e.charCodeAt(0)===111&&e.charCodeAt(1)===110&&(e.charCodeAt(2)>122||97>e.charCodeAt(2)),nr=e=>e.startsWith("onUpdate:"),de=Object.assign,Aa=(e,t)=>{let i=e.indexOf(t);i>-1&&e.splice(i,1)},yp=Object.prototype.hasOwnProperty,fe=(e,t)=>yp.call(e,t),G=Array.isArray,se=e=>typeof e=="function",re=e=>typeof e=="string",Ze=e=>typeof e=="symbol",me=e=>e!==null&&typeof e=="object",Ia=e=>(me(e)||se(e))&&se(e.then)&&se(e.catch),Me=Object.prototype.toString,rr=e=>re(e)&&e!=="NaN"&&e[0]!=="-"&&""+parseInt(e,10)===e,Vt=bt(",key,ref,ref_for,ref_key,onVnodeBeforeMount,onVnodeMounted,onVnodeBeforeUpdate,onVnodeUpdated,onVnodeBeforeUnmount,onVnodeUnmounted"),xp=bt("bind,cloak,else-if,else,for,html,if,model,on,once,pre,show,slot,text,memo"),ar=e=>{let t=Object.create(null);return i=>t[i]||(t[i]=e(i))},wp=/-\w/g,ye=ar(e=>e.replace(wp,t=>t.slice(1).toUpperCase())),kp=/\B([A-Z])/g,dt=ar(e=>e.replace(kp,"-$1").toLowerCase()),Pi=ar(e=>e.charAt(0).toUpperCase()+e.slice(1)),Wi=ar(e=>e?`on${Pi(e)}`:""),De=(e,t)=>!Object.is(e,t),Ji=(e,...t)=>{for(let i=0;i<e.length;i++)e[i](...t)},Mo=(e,t,i,s=!1)=>{Object.defineProperty(e,t,{configurable:!0,enumerable:!1,writable:s,value:i})},lr=e=>{let t=parseFloat(e);return isNaN(t)?e:t},Gi=e=>{let t=re(e)?Number(e):NaN;return isNaN(t)?e:t},or=()=>gl||(gl="u">typeof globalThis?globalThis:"u">typeof self?self:"u">typeof window?window:"u">typeof global?global:{}),_p=bt("Infinity,undefined,NaN,isFinite,isNaN,parseFloat,parseInt,decodeURI,decodeURIComponent,encodeURI,encodeURIComponent,Math,Number,Date,Array,Object,Boolean,String,RegExp,Map,Set,JSON,Intl,BigInt,console,Error,Symbol");function Vs(e){if(G(e)){let t={};for(let i=0;i<e.length;i++){let s=e[i],n=re(s)?Ao(s):Vs(s);if(n)for(let r in n)t[r]=n[r]}return t}if(re(e)||me(e))return e}var Sp=/;(?![^(]*\))/g,qp=/:([^]+)/,Tp=/\/\*[^]*?\*\//g;function Ao(e){let t={};return e.replace(Tp,"").split(Sp).forEach(i=>{if(i){let s=i.split(qp);s.length>1&&(t[s[0].trim()]=s[1].trim())}}),t}function Hs(e){let t="";if(re(e))t=e;else if(G(e))for(let i=0;i<e.length;i++){let s=Hs(e[i]);s&&(t+=s+" ")}else if(me(e))for(let i in e)e[i]&&(t+=i+" ");return t.trim()}function Cp(e){if(!e)return null;let{class:t,style:i}=e;return t&&!re(t)&&(e.class=Hs(t)),i&&(e.style=Vs(i)),e}var Mp=bt("html,body,base,head,link,meta,style,title,address,article,aside,footer,header,hgroup,h1,h2,h3,h4,h5,h6,nav,section,div,dd,dl,dt,figcaption,figure,picture,hr,img,li,main,ol,p,pre,ul,a,b,abbr,bdi,bdo,br,cite,code,data,dfn,em,i,kbd,mark,q,rp,rt,ruby,s,samp,small,span,strong,sub,sup,time,u,var,wbr,area,audio,map,track,video,embed,object,param,source,canvas,script,noscript,del,ins,caption,col,colgroup,table,thead,tbody,td,th,tr,button,datalist,fieldset,form,input,label,legend,meter,optgroup,option,output,progress,select,textarea,details,dialog,menu,summary,template,blockquote,iframe,tfoot"),Ap=bt("svg,animate,animateMotion,animateTransform,circle,clipPath,color-profile,defs,desc,discard,ellipse,feBlend,feColorMatrix,feComponentTransfer,feComposite,feConvolveMatrix,feDiffuseLighting,feDisplacementMap,feDistantLight,feDropShadow,feFlood,feFuncA,feFuncB,feFuncG,feFuncR,feGaussianBlur,feImage,feMerge,feMergeNode,feMorphology,feOffset,fePointLight,feSpecularLighting,feSpotLight,feTile,feTurbulence,filter,foreignObject,g,hatch,hatchpath,image,line,linearGradient,marker,mask,mesh,meshgradient,meshpatch,meshrow,metadata,mpath,path,pattern,polygon,polyline,radialGradient,rect,set,solidcolor,stop,switch,symbol,text,textPath,title,tspan,unknown,use,view"),Ip=bt("annotation,annotation-xml,maction,maligngroup,malignmark,math,menclose,merror,mfenced,mfrac,mfraction,mglyph,mi,mlabeledtr,mlongdiv,mmultiscripts,mn,mo,mover,mpadded,mphantom,mprescripts,mroot,mrow,ms,mscarries,mscarry,msgroup,msline,mspace,msqrt,msrow,mstack,mstyle,msub,msubsup,msup,mtable,mtd,mtext,mtr,munder,munderover,none,semantics"),Np=bt("area,base,br,col,embed,hr,img,input,link,meta,param,source,track,wbr"),Ep=bt("itemscope,allowfullscreen,formnovalidate,ismap,nomodule,novalidate,readonly");function Jt(e,t){let i,s;if(e===t)return!0;let n=(i=e,Me.call(i)==="[object Date]"),r=(s=t,Me.call(s)==="[object Date]");if(n||r)return!!n&&!!r&&e.getTime()===t.getTime();if(n=Ze(e),r=Ze(t),n||r)return e===t;if(n=G(e),r=G(t),n||r)return!!n&&!!r&&function(a,l){if(a.length!==l.length)return!1;let o=!0;for(let c=0;o&&c<a.length;c++)o=Jt(a[c],l[c]);return o}(e,t);if(n=me(e),r=me(t),n||r){if(!n||!r||Object.keys(e).length!==Object.keys(t).length)return!1;for(let a in e){let l=e.hasOwnProperty(a),o=t.hasOwnProperty(a);if(l&&!o||!l&&o||!Jt(e[a],t[a]))return!1}}return String(e)===String(t)}function cr(e,t){return e.findIndex(i=>Jt(i,t))}var Io=e=>!!(e&&e.__v_isRef===!0),No=e=>re(e)?e:e==null?"":G(e)||me(e)&&(e.toString===Me||!se(e.toString))?Io(e)?No(e.value):JSON.stringify(e,Eo,2):String(e),Eo=(e,t)=>{let i;if(Io(t))return Eo(e,t.value);if(i=t,Me.call(i)==="[object Map]")return{[`Map(${t.size})`]:[...t.entries()].reduce((s,[n,r],a)=>(s[Nr(n,a)+" =>"]=r,s),{})};{let s;if(s=t,Me.call(s)==="[object Set]")return{[`Set(${t.size})`]:[...t.values()].map(n=>Nr(n))};{if(Ze(t))return Nr(t);let n;if(me(t)&&!G(t)&&(n=t,Me.call(n)!=="[object Object]"))return String(t)}}return t},Nr=(e,t="")=>{var i;return Ze(e)?`Symbol(${(i=e.description)!=null?i:t})`:e},Ns=class{constructor(t=!1){this.detached=t,this._active=!0,this._on=0,this.effects=[],this.cleanups=[],this._isPaused=!1,this._warnOnRun=!0,this.__v_skip=!0,!t&&Fe&&(Fe.active?(this.parent=Fe,this.index=(Fe.scopes||(Fe.scopes=[])).push(this)-1):(this._active=!1,this._warnOnRun=!1))}get active(){return this._active}pause(){if(this._active){let t,i;if(this._isPaused=!0,this.scopes){let s=this.scopes.slice();for(t=0,i=s.length;t<i;t++)s[t].pause()}for(t=0,i=this.effects.length;t<i;t++)this.effects[t].pause()}}resume(){if(this._active&&this._isPaused){let t,i;if(this._isPaused=!1,this.scopes){let n=this.scopes.slice();for(t=0,i=n.length;t<i;t++)n[t].resume()}let s=this.effects.slice();for(t=0,i=s.length;t<i;t++)s[t].resume()}}run(t){if(this._active){let i=Fe;try{return Fe=this,t()}finally{Fe=i}}}on(){++this._on==1&&(this.prevScope=Fe,Fe=this)}off(){if(this._on>0&&--this._on==0){if(Fe===this)Fe=this.prevScope;else{let t=Fe;for(;t;){if(t.prevScope===this){t.prevScope=this.prevScope;break}t=t.prevScope}}this.prevScope=void 0}}stop(t){if(this._active){let i,s;for(this._active=!1,i=0,s=this.effects.length;i<s;i++)this.effects[i].stop();for(this.effects.length=0,i=0,s=this.cleanups.length;i<s;i++)this.cleanups[i]();if(this.cleanups.length=0,this.scopes){let n=this.scopes.slice();for(i=0,s=n.length;i<s;i++)n[i].stop(!0);this.scopes.length=0}if(!this.detached&&this.parent&&!t){let n=this.parent.scopes.pop();n&&n!==this&&(this.parent.scopes[this.index]=n,n.index=this.index)}this.parent=void 0}}};function Op(e){return new Ns(e)}function Oo(){return Fe}function Rp(e,t=!1){Fe&&Fe.cleanups.push(e)}var Er=new WeakSet,Mi=class{constructor(t){this.fn=t,this.deps=void 0,this.depsTail=void 0,this.flags=5,this.next=void 0,this.cleanup=void 0,this.scheduler=void 0,Fe&&(Fe.active?Fe.effects.push(this):this.flags&=-2)}pause(){this.flags|=64}resume(){64&this.flags&&(this.flags&=-65,Er.has(this)&&(Er.delete(this),this.trigger()))}notify(){(!(2&this.flags)||32&this.flags)&&(8&this.flags||Ro(this))}run(){if(!(1&this.flags))return this.fn();this.flags|=2,bl(this),Po(this);let t=ke,i=Ct;ke=this,Ct=!0;try{return this.fn()}finally{jo(this),ke=t,Ct=i,this.flags&=-3}}stop(){if(1&this.flags){for(let t=this.deps;t;t=t.nextDep)Ea(t);this.deps=this.depsTail=void 0,bl(this),this.onStop&&this.onStop(),this.flags&=-2}}trigger(){64&this.flags?Er.add(this):this.scheduler?this.scheduler():this.runIfDirty()}runIfDirty(){Gr(this)&&this.run()}get dirty(){return Gr(this)}},dr=0;function Ro(e,t=!1){if(e.flags|=8,t){e.next=Ss,Ss=e;return}e.next=_s,_s=e}function Na(){let e;if(!(--dr>0)){if(Ss){let t=Ss;for(Ss=void 0;t;){let i=t.next;t.next=void 0,t.flags&=-9,t=i}}for(;_s;){let t=_s;for(_s=void 0;t;){let i=t.next;if(t.next=void 0,t.flags&=-9,1&t.flags)try{t.trigger()}catch(s){e||(e=s)}t=i}}if(e)throw e}}function Po(e){for(let t=e.deps;t;t=t.nextDep)t.version=-1,t.prevActiveLink=t.dep.activeLink,t.dep.activeLink=t}function jo(e){let t,i=e.depsTail,s=i;for(;s;){let n=s.prevDep;s.version===-1?(s===i&&(i=n),Ea(s),function(r){let{prevDep:a,nextDep:l}=r;a&&(a.nextDep=l,r.prevDep=void 0),l&&(l.prevDep=a,r.nextDep=void 0)}(s)):t=s,s.dep.activeLink=s.prevActiveLink,s.prevActiveLink=void 0,s=n}e.deps=t,e.depsTail=i}function Gr(e){for(let t=e.deps;t;t=t.nextDep)if(t.dep.version!==t.version||t.dep.computed&&(Lo(t.dep.computed)||t.dep.version!==t.version))return!0;return!!e._dirty}function Lo(e){if(4&e.flags&&!(16&e.flags)||(e.flags&=-17,e.globalVersion===Es)||(e.globalVersion=Es,!e.isSSR&&128&e.flags&&(!e.deps&&!e._dirty||!Gr(e))))return;e.flags|=2;let t=e.dep,i=ke,s=Ct;ke=e,Ct=!0;try{Po(e);let n=e.fn(e._value);(t.version===0||De(n,e._value))&&(e.flags|=128,e._value=n,t.version++)}catch(n){throw t.version++,n}finally{ke=i,Ct=s,jo(e),e.flags&=-3}}function Ea(e,t=!1){let{dep:i,prevSub:s,nextSub:n}=e;if(s&&(s.nextSub=n,e.prevSub=void 0),n&&(n.prevSub=s,e.nextSub=void 0),i.subs===e&&(i.subs=s,!s&&i.computed)){i.computed.flags&=-5;for(let r=i.computed.deps;r;r=r.nextDep)Ea(r,!0)}t||--i.sc||!i.map||i.map.delete(i.key)}function Pp(e,t){e.effect instanceof Mi&&(e=e.effect.fn);let i=new Mi(e);t&&de(i,t);try{i.run()}catch(n){throw i.stop(),n}let s=i.run.bind(i);return s.effect=i,s}function jp(e){e.effect.stop()}var Ct=!0,Fo=[];function Gt(){Fo.push(Ct),Ct=!1}function Yt(){let e=Fo.pop();Ct=e===void 0||e}function bl(e){let{cleanup:t}=e;if(e.cleanup=void 0,t){let i=ke;ke=void 0;try{t()}finally{ke=i}}}var Es=0,Yr=class{constructor(t,i){this.sub=t,this.dep=i,this.version=i.version,this.nextDep=this.prevDep=this.nextSub=this.prevSub=this.prevActiveLink=void 0}},ts=class{constructor(t){this.computed=t,this.version=0,this.activeLink=void 0,this.subs=void 0,this.map=void 0,this.key=void 0,this.sc=0,this.__v_skip=!0}track(t){if(!ke||!Ct||ke===this.computed)return;let i=this.activeLink;if(i===void 0||i.sub!==ke)i=this.activeLink=new Yr(ke,this),ke.deps?(i.prevDep=ke.depsTail,ke.depsTail.nextDep=i,ke.depsTail=i):ke.deps=ke.depsTail=i,function s(n){if(n.dep.sc++,4&n.sub.flags){let r=n.dep.computed;if(r&&!n.dep.subs){r.flags|=20;for(let l=r.deps;l;l=l.nextDep)s(l)}let a=n.dep.subs;a!==n&&(n.prevSub=a,a&&(a.nextSub=n)),n.dep.subs=n}}(i);else if(i.version===-1&&(i.version=this.version,i.nextDep)){let s=i.nextDep;s.prevDep=i.prevDep,i.prevDep&&(i.prevDep.nextDep=s),i.prevDep=ke.depsTail,i.nextDep=void 0,ke.depsTail.nextDep=i,ke.depsTail=i,ke.deps===i&&(ke.deps=s)}return i}trigger(t){this.version++,Es++,this.notify(t)}notify(t){dr++;try{for(let i=this.subs;i;i=i.prevSub)i.sub.notify()&&i.sub.dep.notify()}finally{Na()}}},Mn=new WeakMap,Si=Symbol(""),Xr=Symbol(""),Os=Symbol("");function Ye(e,t,i){if(Ct&&ke){let s=Mn.get(e);s||Mn.set(e,s=new Map);let n=s.get(i);n||(s.set(i,n=new ts),n.map=s,n.key=i),n.track()}}function Dt(e,t,i,s,n,r){let a=Mn.get(e);if(!a)return void Es++;let l=o=>{o&&o.trigger()};if(dr++,t==="clear")a.forEach(l);else{let o=G(e),c=o&&rr(i);if(o&&i==="length"){let d=Number(s);a.forEach((p,f)=>{(f==="length"||f===Os||!Ze(f)&&f>=d)&&l(p)})}else switch((i!==void 0||a.has(void 0))&&l(a.get(i)),c&&l(a.get(Os)),t){case"add":if(o)c&&l(a.get("length"));else{let p;l(a.get(Si)),p=e,Me.call(p)==="[object Map]"&&l(a.get(Xr))}break;case"delete":if(!o){let p;l(a.get(Si)),p=e,Me.call(p)==="[object Map]"&&l(a.get(Xr))}break;case"set":let d;d=e,Me.call(d)==="[object Map]"&&l(a.get(Si))}}Na()}function zi(e){let t=ue(e);return t===e?t:(Ye(t,"iterate",Os),ut(e)?t:t.map(Mt))}function pr(e){return Ye(e=ue(e),"iterate",Os),e}function Rt(e,t){return Pt(e)?Ht(e)?Yi(Mt(t)):Yi(t):Mt(t)}var Lp={__proto__:null,[Symbol.iterator](){return Or(this,Symbol.iterator,e=>Rt(this,e))},concat(...e){return zi(this).concat(...e.map(t=>G(t)?zi(t):t))},entries(){return Or(this,"entries",e=>(e[1]=Rt(this,e[1]),e))},every(e,t){return Lt(this,"every",e,t,void 0,arguments)},filter(e,t){return Lt(this,"filter",e,t,i=>i.map(s=>Rt(this,s)),arguments)},find(e,t){return Lt(this,"find",e,t,i=>Rt(this,i),arguments)},findIndex(e,t){return Lt(this,"findIndex",e,t,void 0,arguments)},findLast(e,t){return Lt(this,"findLast",e,t,i=>Rt(this,i),arguments)},findLastIndex(e,t){return Lt(this,"findLastIndex",e,t,void 0,arguments)},forEach(e,t){return Lt(this,"forEach",e,t,void 0,arguments)},includes(...e){return Rr(this,"includes",e)},indexOf(...e){return Rr(this,"indexOf",e)},join(e){return zi(this).join(e)},lastIndexOf(...e){return Rr(this,"lastIndexOf",e)},map(e,t){return Lt(this,"map",e,t,void 0,arguments)},pop(){return ms(this,"pop")},push(...e){return ms(this,"push",e)},reduce(e,...t){return yl(this,"reduce",e,t)},reduceRight(e,...t){return yl(this,"reduceRight",e,t)},shift(){return ms(this,"shift")},some(e,t){return Lt(this,"some",e,t,void 0,arguments)},splice(...e){return ms(this,"splice",e)},toReversed(){return zi(this).toReversed()},toSorted(e){return zi(this).toSorted(e)},toSpliced(...e){return zi(this).toSpliced(...e)},unshift(...e){return ms(this,"unshift",e)},values(){return Or(this,"values",e=>Rt(this,e))}};function Or(e,t,i){let s=pr(e),n=s[t]();return s===e||ut(e)||(n._next=n.next,n.next=()=>{let r=n._next();return r.done||(r.value=i(r.value)),r}),n}var Fp=Array.prototype;function Lt(e,t,i,s,n,r){let a=pr(e),l=a!==e&&!ut(e),o=a[t];if(o!==Fp[t]){let p=o.apply(e,r);return l?Mt(p):p}let c=i;a!==e&&(l?c=function(p,f){return i.call(this,Rt(e,p),f,e)}:i.length>2&&(c=function(p,f){return i.call(this,p,f,e)}));let d=o.call(a,c,s);return l&&n?n(d):d}function yl(e,t,i,s){let n=pr(e),r=n!==e&&!ut(e),a=i,l=!1;n!==e&&(r?(l=s.length===0,a=function(c,d,p){return l&&(l=!1,c=Rt(e,c)),i.call(this,c,Rt(e,d),p,e)}):i.length>3&&(a=function(c,d,p){return i.call(this,c,d,p,e)}));let o=n[t](a,...s);return l?Rt(e,o):o}function Rr(e,t,i){let s=ue(e);Ye(s,"iterate",Os);let n=s[t](...i);return(n===-1||n===!1)&&Ks(i[0])?(i[0]=ue(i[0]),s[t](...i)):n}function ms(e,t,i=[]){Gt(),dr++;let s=ue(e)[t].apply(e,i);return Na(),Yt(),s}var zp=bt("__proto__,__v_isRef,__isVue"),zo=new Set(Object.getOwnPropertyNames(Symbol).filter(e=>e!=="arguments"&&e!=="caller").map(e=>Symbol[e]).filter(Ze));function Bp(e){Ze(e)||(e=String(e));let t=ue(this);return Ye(t,"has",e),t.hasOwnProperty(e)}var An=class{constructor(t=!1,i=!1){this._isReadonly=t,this._isShallow=i}get(t,i,s){if(i==="__v_skip")return t.__v_skip;let n=this._isReadonly,r=this._isShallow;if(i==="__v_isReactive")return!n;if(i==="__v_isReadonly")return n;if(i==="__v_isShallow")return r;if(i==="__v_raw")return s===(n?r?Uo:$o:r?Do:Bo).get(t)||Object.getPrototypeOf(t)===Object.getPrototypeOf(s)?t:void 0;let a=G(t);if(!n){let o;if(a&&(o=Lp[i]))return o;if(i==="hasOwnProperty")return Bp}let l=Reflect.get(t,i,Le(t)?t:s);if((Ze(i)?zo.has(i):zp(i))||(n||Ye(t,"get",i),r))return l;if(Le(l)){let o=a&&rr(i)?l:l.value;return n&&me(o)?En(o):o}return me(l)?n?En(l):ui(l):l}},In=class extends An{constructor(t=!1){super(!1,t)}set(t,i,s,n){let r=t[i],a=G(t)&&rr(i);if(!this._isShallow){let c=Pt(r);if(ut(s)||Pt(s)||(r=ue(r),s=ue(s)),!a&&Le(r)&&!Le(s))return c||(r.value=s),!0}let l=a?Number(i)<t.length:fe(t,i),o=Reflect.set(t,i,s,Le(t)?t:n);return t===ue(n)&&o&&(l?De(s,r)&&Dt(t,"set",i,s):Dt(t,"add",i,s)),o}deleteProperty(t,i){let s=fe(t,i);t[i];let n=Reflect.deleteProperty(t,i);return n&&s&&Dt(t,"delete",i,void 0),n}has(t,i){let s=Reflect.has(t,i);return Ze(i)&&zo.has(i)||Ye(t,"has",i),s}ownKeys(t){return Ye(t,"iterate",G(t)?"length":Si),Reflect.ownKeys(t)}},Nn=class extends An{constructor(t=!1){super(!0,t)}set(t,i){return!0}deleteProperty(t,i){return!0}},Dp=new In,$p=new Nn,Up=new In(!0),Vp=new Nn(!0),Pr=e=>e;function on(e){return function(){return e!=="delete"&&(e==="clear"?void 0:this)}}function ur(e,t){let i,s=(de(i={get(n){let r=this.__v_raw,a=ue(r),l=ue(n);e||(De(n,l)&&Ye(a,"get",n),Ye(a,"get",l));let{has:o}=Reflect.getPrototypeOf(a),c=t?Pr:e?Yi:Mt;return o.call(a,n)?c(r.get(n)):o.call(a,l)?c(r.get(l)):void(r!==a&&r.get(n))},get size(){let n=this.__v_raw;return e||Ye(ue(n),"iterate",Si),n.size},has(n){let r=this.__v_raw,a=ue(r),l=ue(n);return e||(De(n,l)&&Ye(a,"has",n),Ye(a,"has",l)),n===l?r.has(n):r.has(n)||r.has(l)},forEach(n,r){let a=this,l=a.__v_raw,o=ue(l),c=t?Pr:e?Yi:Mt;return e||Ye(o,"iterate",Si),l.forEach((d,p)=>n.call(r,c(d),c(p),a))}},e?{add:on("add"),set:on("set"),delete:on("delete"),clear:on("clear")}:{add(n){let r=ue(this),a=Reflect.getPrototypeOf(r),l=ue(n),o=t||ut(n)||Pt(n)?n:l;return a.has.call(r,o)||De(n,o)&&a.has.call(r,n)||De(l,o)&&a.has.call(r,l)||(r.add(o),Dt(r,"add",o,o)),this},set(n,r){t||ut(r)||Pt(r)||(r=ue(r));let a=ue(this),{has:l,get:o}=Reflect.getPrototypeOf(a),c=l.call(a,n);c||(n=ue(n),c=l.call(a,n));let d=o.call(a,n);return a.set(n,r),c?De(r,d)&&Dt(a,"set",n,r):Dt(a,"add",n,r),this},delete(n){let r=ue(this),{has:a,get:l}=Reflect.getPrototypeOf(r),o=a.call(r,n);o||(n=ue(n),o=a.call(r,n)),l&&l.call(r,n);let c=r.delete(n);return o&&Dt(r,"delete",n,void 0),c},clear(){let n=ue(this),r=n.size!==0,a=n.clear();return r&&Dt(n,"clear",void 0,void 0),a}}),["keys","values","entries",Symbol.iterator].forEach(n=>{i[n]=function(...r){let a,l=this.__v_raw,o=ue(l),c=(a=o,Me.call(a)==="[object Map]"),d=n==="entries"||n===Symbol.iterator&&c,p=l[n](...r),f=t?Pr:e?Yi:Mt;return e||Ye(o,"iterate",n==="keys"&&c?Xr:Si),de(Object.create(p),{next(){let{value:y,done:m}=p.next();return m?{value:y,done:m}:{value:d?[f(y[0]),f(y[1])]:f(y),done:m}}})}}),i);return(n,r,a)=>r==="__v_isReactive"?!e:r==="__v_isReadonly"?e:r==="__v_raw"?n:Reflect.get(fe(s,r)&&r in n?s:n,r,a)}var Hp={get:ur(!1,!1)},Kp={get:ur(!1,!0)},Qp={get:ur(!0,!1)},Wp={get:ur(!0,!0)},Bo=new WeakMap,Do=new WeakMap,$o=new WeakMap,Uo=new WeakMap;function ui(e){return Pt(e)?e:hr(e,!1,Dp,Hp,Bo)}function Vo(e){return hr(e,!1,Up,Kp,Do)}function En(e){return hr(e,!0,$p,Qp,$o)}function Jp(e){return hr(e,!0,Vp,Wp,Uo)}function hr(e,t,i,s,n){let r;if(!me(e)||e.__v_raw&&!(t&&e.__v_isReactive)||e.__v_skip||!Object.isExtensible(e))return e;let a=n.get(e);if(a)return a;let l=function(c){switch(c){case"Object":case"Array":return 1;case"Map":case"Set":case"WeakMap":case"WeakSet":return 2;default:return 0}}((r=e,Me.call(r)).slice(8,-1));if(l===0)return e;let o=new Proxy(e,l===2?s:i);return n.set(e,o),o}function Ht(e){return Pt(e)?Ht(e.__v_raw):!!(e&&e.__v_isReactive)}function Pt(e){return!!(e&&e.__v_isReadonly)}function ut(e){return!!(e&&e.__v_isShallow)}function Ks(e){return!!e&&!!e.__v_raw}function ue(e){let t=e&&e.__v_raw;return t?ue(t):e}function Ho(e){return!fe(e,"__v_skip")&&Object.isExtensible(e)&&Mo(e,"__v_skip",!0),e}var Mt=e=>me(e)?ui(e):e,Yi=e=>me(e)?En(e):e;function Le(e){return!!e&&e.__v_isRef===!0}function qs(e){return Qo(e,!1)}function Ko(e){return Qo(e,!0)}function Qo(e,t){return Le(e)?e:new Zr(e,t)}var Zr=class{constructor(t,i){this.dep=new ts,this.__v_isRef=!0,this.__v_isShallow=!1,this._rawValue=i?t:ue(t),this._value=i?t:Mt(t),this.__v_isShallow=i}get value(){return this.dep.track(),this._value}set value(t){let i=this._rawValue,s=this.__v_isShallow||ut(t)||Pt(t);De(t=s?t:ue(t),i)&&(this._rawValue=t,this._value=s?t:Mt(t),this.dep.trigger())}};function Gp(e){e.dep&&e.dep.trigger()}function Qs(e){return Le(e)?e.value:e}function Yp(e){return se(e)?e():Qs(e)}var Xp={get:(e,t,i)=>t==="__v_raw"?e:Qs(Reflect.get(e,t,i)),set:(e,t,i,s)=>{let n=e[t];return Le(n)&&!Le(i)?(n.value=i,!0):Reflect.set(e,t,i,s)}};function Oa(e){return Ht(e)?e:new Proxy(e,Xp)}var ea=class{constructor(t){this.__v_isRef=!0,this._value=void 0;let i=this.dep=new ts,{get:s,set:n}=t(i.track.bind(i),i.trigger.bind(i));this._get=s,this._set=n}get value(){return this._value=this._get()}set value(t){this._set(t)}};function Wo(e){return new ea(e)}function Zp(e){let t=G(e)?Array(e.length):{};for(let i in e)t[i]=new On(e,i,void 0);return t}var On=class{constructor(t,i,s){this._object=t,this._defaultValue=s,this.__v_isRef=!0,this._value=void 0,this._key=Ze(i)?i:String(i),this._raw=ue(t);let n=!0,r=t;if(!G(t)||Ze(this._key)||!rr(this._key))do n=!Ks(r)||ut(r);while(n&&(r=r.__v_raw));this._shallow=n}get value(){let t=this._object[this._key];return this._shallow&&(t=Qs(t)),this._value=t===void 0?this._defaultValue:t}set value(t){if(this._shallow&&Le(this._raw[this._key])){let i=this._object[this._key];if(Le(i)){i.value=t;return}}this._object[this._key]=t}get dep(){var t,i;let s;return t=this._raw,i=this._key,(s=Mn.get(t))&&s.get(i)}},ta=class{constructor(t){this._getter=t,this.__v_isRef=!0,this.__v_isReadonly=!0,this._value=void 0}get value(){return this._value=this._getter()}};function eu(e,t,i){return Le(e)?e:se(e)?new ta(e):!me(e)||!(arguments.length>1)?qs(e):new On(e,t,i)}var ia=class{constructor(t,i,s){this.fn=t,this.setter=i,this._value=void 0,this.dep=new ts(this),this.__v_isRef=!0,this.deps=void 0,this.depsTail=void 0,this.flags=16,this.globalVersion=Es-1,this.next=void 0,this.effect=this,this.__v_isReadonly=!i,this.isSSR=s}notify(){if(this.flags|=16,!(8&this.flags)&&ke!==this)return Ro(this,!0),!0}get value(){let t=this.dep.track();return Lo(this),t&&(t.version=this.dep.version),this._value}set value(t){this.setter&&this.setter(t)}},tu={GET:"get",HAS:"has",ITERATE:"iterate"},iu={SET:"set",ADD:"add",DELETE:"delete",CLEAR:"clear"},cn={},Rn=new WeakMap;function su(){return ai}function Jo(e,t=!1,i=ai){if(i){let s=Rn.get(i);s||Rn.set(i,s=[]),s.push(e)}}function $t(e,t=1/0,i){if(t<=0||!me(e)||e.__v_skip||((i=i||new Map).get(e)||0)>=t)return e;if(i.set(e,t),t--,Le(e))$t(e.value,t,i);else if(G(e))for(let s=0;s<e.length;s++)$t(e[s],t,i);else{let s,n;if(s=e,Me.call(s)==="[object Set]"||(n=e,Me.call(n)==="[object Map]"))e.forEach(r=>{$t(r,t,i)});else{let r;if(r=e,Me.call(r)==="[object Object]"){for(let a in e)$t(e[a],t,i);for(let a of Object.getOwnPropertySymbols(e))Object.prototype.propertyIsEnumerable.call(e,a)&&$t(e[a],t,i)}}}return e}function nu(e,t){}var ru={SETUP_FUNCTION:0,0:"SETUP_FUNCTION",RENDER_FUNCTION:1,1:"RENDER_FUNCTION",NATIVE_EVENT_HANDLER:5,5:"NATIVE_EVENT_HANDLER",COMPONENT_EVENT_HANDLER:6,6:"COMPONENT_EVENT_HANDLER",VNODE_HOOK:7,7:"VNODE_HOOK",DIRECTIVE_HOOK:8,8:"DIRECTIVE_HOOK",TRANSITION_HOOK:9,9:"TRANSITION_HOOK",APP_ERROR_HANDLER:10,10:"APP_ERROR_HANDLER",APP_WARN_HANDLER:11,11:"APP_WARN_HANDLER",FUNCTION_REF:12,12:"FUNCTION_REF",ASYNC_COMPONENT_LOADER:13,13:"ASYNC_COMPONENT_LOADER",SCHEDULER:14,14:"SCHEDULER",COMPONENT_UPDATE:15,15:"COMPONENT_UPDATE",APP_UNMOUNT_CLEANUP:16,16:"APP_UNMOUNT_CLEANUP"};function ls(e,t,i,s){try{return s?e(...s):e()}catch(n){ji(n,t,i)}}function vt(e,t,i,s){if(se(e)){let n=ls(e,t,i,s);return n&&Ia(n)&&n.catch(r=>{ji(r,t,i)}),n}if(G(e)){let n=[];for(let r=0;r<e.length;r++)n.push(vt(e[r],t,i,s));return n}}function ji(e,t,i,s=!0){let n=t?t.vnode:null,{errorHandler:r,throwUnhandledErrorInProduction:a}=t&&t.appContext.config||pe;if(t){let l=t.parent,o=t.proxy,c=`https://vuejs.org/error-reference/#runtime-${i}`;for(;l;){let d=l.ec;if(d){for(let p=0;p<d.length;p++)if(d[p](e,o,c)===!1)return}l=l.parent}if(r){Gt(),ls(r,null,10,[e,o,c]),Yt();return}}(function(l,o=!0,c=!1){if(c)throw l;console.error(l)})(e,s,a)}var nt=[],Et=-1,Xi=[],li=null,Di=0,Go=Promise.resolve(),kn=null;function mr(e){let t=kn||Go;return e?t.then(this?e.bind(this):e):t}function Ra(e){if(!(1&e.flags)){let t=Ts(e),i=nt[nt.length-1];!i||!(2&e.flags)&&t>=Ts(i)?nt.push(e):nt.splice(function(s){let n=Et+1,r=nt.length;for(;n<r;){let a=n+r>>>1,l=nt[a],o=Ts(l);o<s||o===s&&2&l.flags?n=a+1:r=a}return n}(t),0,e),e.flags|=1,Yo()}}function Yo(){kn||(kn=Go.then(function e(t){try{for(Et=0;Et<nt.length;Et++){let i=nt[Et];i&&!(8&i.flags)&&(4&i.flags&&(i.flags&=-2),ls(i,i.i,i.i?15:14),4&i.flags||(i.flags&=-2))}}finally{for(;Et<nt.length;Et++){let i=nt[Et];i&&(i.flags&=-2)}Et=-1,nt.length=0,Pn(),kn=null,(nt.length||Xi.length)&&e()}}))}function Rs(e){G(e)?Xi.push(...e):li&&e.id===-1?li.splice(Di+1,0,e):1&e.flags||(Xi.push(e),e.flags|=1),Yo()}function xl(e,t,i=Et+1){for(;i<nt.length;i++){let s=nt[i];if(s&&2&s.flags){if(e&&s.id!==e.uid)continue;nt.splice(i,1),i--,4&s.flags&&(s.flags&=-2),s(),4&s.flags||(s.flags&=-2)}}}function Pn(e){if(Xi.length){let t=[...new Set(Xi)].sort((i,s)=>Ts(i)-Ts(s));if(Xi.length=0,li)return void li.push(...t);for(li=t,Di=0;Di<li.length;Di++){let i=li[Di];4&i.flags&&(i.flags&=-2),8&i.flags||i(),i.flags&=-2}li=null,Di=0}}var Ts=e=>e.id==null?2&e.flags?-1:1/0:e.id,Qe=null,fr=null;function Ps(e){let t=Qe;return Qe=e,fr=e&&e.type.__scopeId||null,t}function au(e){fr=e}function lu(){fr=null}var ou=e=>Pa;function Pa(e,t=Qe,i){if(!t||e._n)return e;let s=(...n)=>{let r;s._d&&Fs(-1);let a=Ps(t),l=Qt.length;try{r=e(...n)}finally{for(let o=Qt.length;o>l;o--)xr();Ps(a),s._d&&Fs(1)}return r};return s._n=!0,s._c=!0,s._d=!0,s}function cu(e,t){if(Qe===null)return e;let i=Xs(Qe),s=e.dirs||(e.dirs=[]);for(let n=0;n<t.length;n++){let[r,a,l,o=pe]=t[n];r&&(se(r)&&(r={mounted:r,updated:r}),r.deep&&$t(a),s.push({dir:r,instance:i,value:a,oldValue:void 0,arg:l,modifiers:o}))}return e}function Ot(e,t,i,s){let n=e.dirs,r=t&&t.dirs;for(let a=0;a<n.length;a++){let l=n[a];r&&(l.oldValue=r[a].value);let o=l.dir[s];o&&(Gt(),vt(o,i,8,[e.el,l,e,t]),Yt())}}function Xo(e,t){if(Ke){let i=Ke.provides,s=Ke.parent&&Ke.parent.provides;s===i&&(i=Ke.provides=Object.create(s)),i[e]=t}}function Cs(e,t,i=!1){let s=rt();if(s||qi){let n=qi?qi._context.provides:s?s.parent==null||s.ce?s.vnode.appContext&&s.vnode.appContext.provides:s.parent.provides:void 0;if(n&&e in n)return n[e];if(arguments.length>1)return i&&se(t)?t.call(s&&s.proxy):t}}function du(){return!!(rt()||qi)}var Zo=Symbol.for("v-scx"),ec=()=>Cs(Zo);function pu(e,t){return Ws(e,null,t)}function uu(e,t){return Ws(e,null,{flush:"post"})}function tc(e,t){return Ws(e,null,{flush:"sync"})}function Zi(e,t,i){return Ws(e,t,i)}function Ws(e,t,i=pe){let s,{immediate:n,flush:r}=i,a=de({},i),l=t&&n||!t&&r!=="post";if(Ii){if(r==="sync"){let p=ec();s=p.__watcherHandles||(p.__watcherHandles=[])}else if(!l){let p=()=>{};return p.stop=He,p.resume=He,p.pause=He,p}}let o=Ke;a.call=(p,f,y)=>vt(p,o,f,y);let c=!1;r==="post"?a.scheduler=p=>{Pe(p,o&&o.suspense)}:r!=="sync"&&(c=!0,a.scheduler=(p,f)=>{f?p():Ra(p)}),a.augmentJob=p=>{t&&(p.flags|=4),c&&(p.flags|=2,o&&(p.id=o.uid,p.i=o))};let d=function(p,f,y=pe){let m,x,q,b,{immediate:u,deep:h,once:g,scheduler:_,augmentJob:k,call:S}=y,C=M=>h?M:ut(M)||h===!1||h===0?$t(M,1):$t(M),E=!1,O=!1;if(Le(p)?(x=()=>p.value,E=ut(p)):Ht(p)?(x=()=>C(p),E=!0):G(p)?(O=!0,E=p.some(M=>Ht(M)||ut(M)),x=()=>p.map(M=>Le(M)?M.value:Ht(M)?C(M):se(M)?S?S(M,2):M():void 0)):x=se(p)?f?S?()=>S(p,2):p:()=>{if(q){Gt();try{q()}finally{Yt()}}let M=ai;ai=m;try{return S?S(p,3,[b]):p(b)}finally{ai=M}}:He,f&&h){let M=x,Q=h===!0?1/0:h;x=()=>$t(M(),Q)}let B=Oo(),T=()=>{m.stop(),B&&B.active&&Aa(B.effects,m)};if(g&&f){let M=f;f=(...Q)=>{let V=M(...Q);return T(),V}}let F=O?Array(p.length).fill(cn):cn,L=M=>{if(1&m.flags&&(m.dirty||M))if(f){let Q=m.run();if(M||h||E||(O?Q.some((V,J)=>De(V,F[J])):De(Q,F))){q&&q();let V=ai;ai=m;try{let J=[Q,F===cn?void 0:O&&F[0]===cn?[]:F,b];F=Q,S?S(f,3,J):f(...J)}finally{ai=V}}}else m.run()};return k&&k(L),(m=new Mi(x)).scheduler=_?()=>_(L,!1):L,b=M=>Jo(M,!1,m),q=m.onStop=()=>{let M=Rn.get(m);if(M){if(S)S(M,4);else for(let Q of M)Q();Rn.delete(m)}},f?u?L(!0):F=m.run():_?_(L.bind(null,!0),!0):m.run(),T.pause=m.pause.bind(m),T.resume=m.resume.bind(m),T.stop=T,T}(e,t,a);return Ii&&(s?s.push(d):l&&d()),d}function hu(e,t,i){let s,n=this.proxy,r=re(e)?e.includes(".")?ic(n,e):()=>n[e]:e.bind(n,n);se(t)?s=t:(s=t.handler,i=t);let a=os(this),l=Ws(r,s.bind(n),i);return a(),l}function ic(e,t){let i=t.split(".");return()=>{let s=e;for(let n=0;n<i.length&&s;n++)s=s[i[n]];return s}}var ni=new WeakMap,sc=Symbol("_vte"),yi=e=>e&&(e.disabled||e.disabled===""),wl=e=>"u">typeof SVGElement&&e instanceof SVGElement,kl=e=>typeof MathMLElement=="function"&&e instanceof MathMLElement,jr=(e,t)=>{let i=e&&e.to;return re(i)?t?t(i):null:i};function dn(e,t,i,{o:{insert:s},m:n},r=2){r===0&&s(e.targetAnchor,t,i);let{el:a,anchor:l,shapeFlag:o,children:c,props:d}=e,p=r===2;if(p&&s(a,t,i),!ni.has(e)&&(!p||yi(d))&&16&o)for(let f=0;f<c.length;f++)n(c[f],t,i,2);p&&s(l,t,i)}var mu={name:"Teleport",__isTeleport:!0,process(e,t,i,s,n,r,a,l,o,c){let{mc:d,pc:p,pbc:f,o:{insert:y,querySelector:m,createText:x,parentNode:q}}=c,b=yi(t.props),{dynamicChildren:u}=t,h=(k,S,C)=>{16&k.shapeFlag&&d(k.children,S,C,n,r,a,l,o)},g=(k=t)=>{let S=yi(k.props),C=k.target=jr(k.props,m),E=Lr(C,k,x,y);C&&(a!=="svg"&&wl(C)?a="svg":a!=="mathml"&&kl(C)&&(a="mathml"),n&&n.isCE&&(n.ce._teleportTargets||(n.ce._teleportTargets=new Set)).add(C),S||(h(k,C,E),fs(k,!1)))},_=k=>{let S=()=>{if(ni.get(k)===S){if(ni.delete(k),yi(k.props)){let C=q(k.el)||i;h(k,C,k.anchor),fs(k,!0)}g(k)}};ni.set(k,S),Pe(S,r)};if(e==null){let k,S=t.el=x(""),C=t.anchor=x("");if(y(S,i,s),y(C,i,s),(k=t.props)&&(k.defer||k.defer==="")||r&&r.pendingBranch)return void _(t);b&&(h(t,i,C),fs(t,!0)),g()}else{t.el=e.el;let k=t.anchor=e.anchor,S=ni.get(e);if(S){S.flags|=8,ni.delete(e),_(t);return}t.targetStart=e.targetStart;let C=t.target=e.target,E=t.targetAnchor=e.targetAnchor,O=yi(e.props),B=O?i:C,T=O?k:E;if(a==="svg"||wl(C)?a="svg":(a==="mathml"||kl(C))&&(a="mathml"),u?(f(e.dynamicChildren,u,B,n,r,a,l),Qa(e,t,!0)):o||p(e,t,B,T,n,r,a,l,!1),b)O?t.props&&e.props&&t.props.to!==e.props.to&&(t.props.to=e.props.to):dn(t,i,k,c,1);else if((t.props&&t.props.to)!==(e.props&&e.props.to)){let F=jr(t.props,m);F&&(t.target=F,dn(t,F,null,c,0))}else O&&dn(t,C,E,c,1);fs(t,b)}},remove(e,t,i,{um:s,o:{remove:n}},r){let{shapeFlag:a,children:l,anchor:o,targetStart:c,targetAnchor:d,target:p,props:f}=e,y=yi(f),m=r||!y,x=ni.get(e);if(x&&(x.flags|=8,ni.delete(e)),p&&(n(c),n(d)),r&&n(o),!x&&(y||p)&&16&a)for(let q=0;q<l.length;q++){let b=l[q];s(b,t,i,m,!!b.dynamicChildren)}},move:dn,hydrate:function(e,t,i,s,n,r,{o:{nextSibling:a,parentNode:l,querySelector:o,insert:c,createText:d}},p){function f(q,b){let u=b;for(;u;){if(u&&u.nodeType===8){if(u.data==="teleport start anchor")t.targetStart=u;else if(u.data==="teleport anchor"){t.targetAnchor=u,q._lpa=t.targetAnchor&&a(t.targetAnchor);break}}u=a(u)}}function y(q,b){b.anchor=p(a(q),b,l(q),i,s,n,r)}let m=t.target=jr(t.props,o),x=yi(t.props);if(m){let q=m._lpa||m.firstChild;16&t.shapeFlag&&(x?(y(e,t),f(m,q),t.targetAnchor||Lr(m,t,d,c,l(e)===m?e:null)):(t.anchor=a(e),f(m,q),t.targetAnchor||Lr(m,t,d,c),p(q&&a(q),t,m,i,s,n,r))),fs(t,x)}else x&&16&t.shapeFlag&&(y(e,t),t.targetStart=e,t.targetAnchor=a(e));return t.anchor&&a(t.anchor)}};function fs(e,t){let i=e.ctx;if(i&&i.ut){let s,n;for(t?(s=e.el,n=e.anchor):(s=e.targetStart,n=e.targetAnchor);s&&s!==n;)s.nodeType===1&&s.setAttribute("data-v-owner",i.uid),s=s.nextSibling;i.ut()}}function Lr(e,t,i,s,n=null){let r=t.targetStart=i(""),a=t.targetAnchor=i("");return r[sc]=a,e&&(s(r,e,n),s(a,e,n)),a}var kt=Symbol("_leaveCb"),vs=Symbol("_enterCb");function ja(){let e={isMounted:!1,isLeaving:!1,isUnmounting:!1,leavingVNodes:new Map};return Gs(()=>{e.isMounted=!0}),br(()=>{e.isUnmounting=!0}),e}var wt=[Function,Array],La={mode:String,appear:Boolean,persisted:Boolean,onBeforeEnter:wt,onEnter:wt,onAfterEnter:wt,onEnterCancelled:wt,onBeforeLeave:wt,onLeave:wt,onAfterLeave:wt,onLeaveCancelled:wt,onBeforeAppear:wt,onAppear:wt,onAfterAppear:wt,onAppearCancelled:wt},nc=e=>{let t=e.subTree;return t.component?nc(t.component):t};function rc(e){let t=e[0];if(e.length>1){for(let i of e)if(i.type!==Re){t=i;break}}return t}var ac={name:"BaseTransition",props:La,setup(e,{slots:t}){let i=rt(),s=ja();return()=>{let n=t.default&&vr(t.default(),!0),r=n&&n.length?rc(n):i.subTree?Oc():void 0;if(!r)return;let a=ue(e),{mode:l}=a;if(s.isLeaving)return Fr(r);let o=_l(r);if(!o)return Fr(r);let c=is(o,a,s,i,p=>c=p);o.type!==Re&&Xt(o,c);let d=i.subTree&&_l(i.subTree);if(d&&d.type!==Re&&!Tt(d,o)&&nc(i).type!==Re){let p=is(d,a,s,i);if(Xt(d,p),l==="out-in"&&o.type!==Re)return s.isLeaving=!0,p.afterLeave=()=>{s.isLeaving=!1,8&i.job.flags||i.update(),delete p.afterLeave,d=void 0},Fr(r);l==="in-out"&&o.type!==Re?p.delayLeave=(f,y,m)=>{lc(s,d)[String(d.key)]=d,f[kt]=()=>{y(),f[kt]=void 0,delete c.delayedLeave,d=void 0},c.delayedLeave=()=>{m(),delete c.delayedLeave,d=void 0}}:d=void 0}else d&&(d=void 0);return r}}};function lc(e,t){let{leavingVNodes:i}=e,s=i.get(t.type);return s||(s=Object.create(null),i.set(t.type,s)),s}function is(e,t,i,s,n){let{appear:r,mode:a,persisted:l=!1,onBeforeEnter:o,onEnter:c,onAfterEnter:d,onEnterCancelled:p,onBeforeLeave:f,onLeave:y,onAfterLeave:m,onLeaveCancelled:x,onBeforeAppear:q,onAppear:b,onAfterAppear:u,onAppearCancelled:h}=t,g=String(e.key),_=lc(i,e),k=(E,O)=>{E&&vt(E,s,9,O)},S=(E,O)=>{let B=O[1];k(E,O),G(E)?E.every(T=>T.length<=1)&&B():E.length<=1&&B()},C={mode:a,persisted:l,beforeEnter(E){let O=o;if(!i.isMounted)if(r)O=q||o;else return;E[kt]&&E[kt](!0);let B=_[g];B&&Tt(e,B)&&B.el[kt]&&B.el[kt](),k(O,[E])},enter(E){if(_[g]===e)return;let O=c,B=d,T=p;if(!i.isMounted)if(r)O=b||c,B=u||d,T=h||p;else return;let F=!1;E[vs]=M=>{F||(F=!0,M?k(T,[E]):k(B,[E]),C.delayedLeave&&C.delayedLeave(),E[vs]=void 0)};let L=E[vs].bind(null,!1);O?S(O,[E,L]):L()},leave(E,O){let B=String(e.key);if(E[vs]&&E[vs](!0),i.isUnmounting)return O();k(f,[E]);let T=!1;E[kt]=L=>{T||(T=!0,O(),L?k(x,[E]):k(m,[E]),E[kt]=void 0,_[B]===e&&delete _[B])};let F=E[kt].bind(null,!1);_[B]=e,y?S(y,[E,F]):F()},clone(E){let O=is(E,t,i,s,n);return n&&n(O),O}};return C}function Fr(e){if(Js(e))return(e=jt(e)).children=null,e}function _l(e){if(!Js(e))return e.type.__isTeleport&&e.children?rc(e.children):e;if(e.component)return e.component.subTree;let{shapeFlag:t,children:i}=e;if(i){if(16&t)return i[0];if(32&t&&se(i.default))return i.default()}}function Xt(e,t){6&e.shapeFlag&&e.component?(e.transition=t,Xt(e.component.subTree,t)):128&e.shapeFlag?(e.ssContent.transition=t.clone(e.ssContent),e.ssFallback.transition=t.clone(e.ssFallback)):e.transition=t}function vr(e,t=!1,i){let s=[],n=0;for(let r=0;r<e.length;r++){let a=e[r],l=i==null?a.key:String(i)+String(a.key!=null?a.key:r);a.type===$e?(128&a.patchFlag&&n++,s=s.concat(vr(a.children,t,l))):(t||a.type!==Re)&&s.push(l!=null?jt(a,{key:l}):a)}if(n>1)for(let r=0;r<s.length;r++)s[r].patchFlag=-2;return s}function Fa(e,t){return se(e)?de({name:e.name},t,{setup:e}):e}function fu(){let e=rt();return e?(e.appContext.config.idPrefix||"v")+"-"+e.ids[0]+e.ids[1]++:""}function za(e){e.ids=[e.ids[0]+e.ids[2]+++"-",0,0]}function vu(e){let t=rt(),i=Ko(null);return t&&Object.defineProperty(t.refs===pe?t.refs={}:t.refs,e,{enumerable:!0,get:()=>i.value,set:s=>i.value=s}),i}function Sl(e,t){let i;return!!((i=Object.getOwnPropertyDescriptor(e,t))&&!i.configurable)}var jn=new WeakMap;function es(e,t,i,s,n=!1){if(G(e))return void e.forEach((x,q)=>es(x,t&&(G(t)?t[q]:t),i,s,n));if(Kt(s)&&!n){512&s.shapeFlag&&s.type.__asyncResolved&&s.component.subTree.component&&es(e,t,i,s.component.subTree);return}let r=4&s.shapeFlag?Xs(s.component):s.el,a=n?null:r,{i:l,r:o}=e,c=t&&t.r,d=l.refs===pe?l.refs={}:l.refs,p=l.setupState,f=ue(p),y=p===pe?$i:x=>!Sl(d,x)&&fe(f,x),m=(x,q)=>!(q&&Sl(d,q));if(c!=null&&c!==o&&(ql(t),re(c)?(d[c]=null,y(c)&&(p[c]=null)):Le(c)&&(m(c,t.k)&&(c.value=null),t.k&&(d[t.k]=null))),se(o))ls(o,l,12,[a,d]);else{let x=re(o),q=Le(o);if(x||q){let b=()=>{if(e.f){let u=x?y(o)?p[o]:d[o]:m()||!e.k?o.value:d[e.k];if(n)G(u)&&Aa(u,r);else if(G(u))u.includes(r)||u.push(r);else if(x)d[o]=[r],y(o)&&(p[o]=d[o]);else{let h=[r];m(o,e.k)&&(o.value=h),e.k&&(d[e.k]=h)}}else x?(d[o]=a,y(o)&&(p[o]=a)):q&&(m(o,e.k)&&(o.value=a),e.k&&(d[e.k]=a))};if(a){let u=()=>{b(),jn.delete(e)};u.id=-1,jn.set(e,u),Pe(u,i)}else ql(e),b()}}}function ql(e){let t=jn.get(e);t&&(t.flags|=8,jn.delete(e))}var Tl=!1,Bi=()=>{Tl||(console.error("Hydration completed but contains mismatches."),Tl=!0)},pn=e=>{if(e.nodeType===1){if(e.namespaceURI.includes("svg")&&e.tagName!=="foreignObject")return"svg";if(e.namespaceURI.includes("MathML"))return"mathml"}},Ui=e=>e.nodeType===8;function gu(e){let{mt:t,p:i,o:{patchProp:s,createText:n,nextSibling:r,parentNode:a,remove:l,insert:o,createComment:c}}=e,d=(u,h,g,_,k,S=!1)=>{S=S||!!h.dynamicChildren;let C=Ui(u)&&u.data==="[",E=()=>m(u,h,g,_,k,C),{type:O,ref:B,shapeFlag:T,patchFlag:F}=h,L=u.nodeType;h.el=u,F===-2&&(S=!1,h.dynamicChildren=null);let M=null;switch(O){case oi:L!==3?h.children===""?(o(h.el=n(""),a(u),u),M=u):M=E():(u.data!==h.children&&(Bi(),u.data=h.children),M=r(u));break;case Re:b(u)?(M=r(u),q(h.el=u.content.firstChild,u,g)):M=L!==8||C?E():r(u);break;case Ti:if(C&&(L=(u=r(u)).nodeType),L===1||L===3){M=u;let Q=!h.children.length;for(let V=0;V<h.staticCount;V++)Q&&(h.children+=M.nodeType===1?M.outerHTML:M.data),V===h.staticCount-1&&(h.anchor=M),M=r(M);return C?r(M):M}E();break;case $e:M=C?y(u,h,g,_,k,S):E();break;default:if(1&T)M=L===1&&h.type.toLowerCase()===u.tagName.toLowerCase()||b(u)?p(u,h,g,_,k,S):E();else if(6&T){h.slotScopeIds=k;let Q=a(u);if(M=C?x(u):Ui(u)&&u.data==="teleport start"?x(u,u.data,"teleport end"):r(u),t(h,Q,null,g,_,pn(Q),S),Kt(h)&&!h.type.__asyncResolved){let V;C?(V=Te($e)).anchor=M?M.previousSibling:Q.lastChild:V=u.nodeType===3?Ja(""):Te("div"),V.el=u,h.component.subTree=V}}else 64&T?M=L!==8?E():h.type.hydrate(u,h,g,_,k,S,e,f):128&T&&(M=h.type.hydrate(u,h,g,_,pn(a(u)),k,S,e,d))}return B!=null&&es(B,null,_,h),M},p=(u,h,g,_,k,S)=>{S=S||!!h.dynamicChildren;let{type:C,dynamicProps:E,props:O,patchFlag:B,shapeFlag:T,dirs:F,transition:L}=h,M=C==="input"||C==="option",Q=!!E;if(M||Q||B!==-1){let V;F&&Ot(h,null,g,"created");let J=!1;if(b(u)){J=Mc(null,L)&&g&&g.vnode.props&&g.vnode.props.appear;let K=u.content.firstChild;if(J){let te=K.getAttribute("class");te&&(K.$cls=te),L.beforeEnter(K)}q(K,u,g),h.el=u=K}if(16&T&&!(O&&(O.innerHTML||O.textContent))){let K=f(u.firstChild,h,u,g,_,k,S);for(K&&!un(u,1)&&Bi();K;){let te=K;K=K.nextSibling,l(te)}}else if(8&T){let K=h.children;K[0]===`
`&&(u.tagName==="PRE"||u.tagName==="TEXTAREA")&&(K=K.slice(1));let{textContent:te}=u;te!==K&&te!==K.replace(/\r\n|\r/g,`
`)&&(un(u,0)||Bi(),u.textContent=h.children)}if(O){if(M||Q||!S||48&B){let K=u.tagName.includes("-"),te=u.namespaceURI.includes("svg")?"svg":u.namespaceURI.includes("MathML")?"mathml":void 0;for(let ne in O)(M&&(ne.endsWith("value")||ne==="indeterminate")||Ri(ne)&&!Vt(ne)||ne[0]==="."||K&&!Vt(ne)||E&&E.includes(ne))&&s(u,ne,null,O[ne],te,g)}else if(O.onClick)s(u,"onClick",null,O.onClick,void 0,g);else if(4&B&&Ht(O.style))for(let K in O.style)O.style[K]}(V=O&&O.onVnodeBeforeMount)&&ot(V,g,h),F&&Ot(h,null,g,"beforeMount"),((V=O&&O.onVnodeMounted)||F||J)&&Ac(()=>{V&&ot(V,g,h),J&&L.enter(u),F&&Ot(h,null,g,"mounted")},_)}return u.nextSibling},f=(u,h,g,_,k,S,C)=>{C=C||!!h.dynamicChildren;let E=h.children,O=E.length,B=!1;for(let T=0;T<O;T++){let F=C?E[T]:E[T]=ct(E[T]),L=F.type===oi;u?(L&&!C&&T+1<O&&ct(E[T+1]).type===oi&&(o(n(u.data.slice(F.children.length)),g,r(u)),u.data=F.children),u=d(u,F,_,k,S,C)):L&&!F.children?o(F.el=n(""),g):(!B&&(B=!0,un(g,1)||Bi()),i(null,F,g,null,_,k,pn(g),S))}return u},y=(u,h,g,_,k,S)=>{let{slotScopeIds:C}=h;C&&(k=k?k.concat(C):C);let E=a(u),O=f(r(u),h,E,g,_,k,S);return O&&Ui(O)&&O.data==="]"?r(h.anchor=O):(Bi(),o(h.anchor=c("]"),E,O),O)},m=(u,h,g,_,k,S)=>{var C,E,O;if(C=u,E=h,un(C.parentElement,1)||(O=C).nodeType===1&&sa(O.getAttribute(Ln),1)||function({props:F}){let L=F&&F[Ln];return typeof L=="string"&&sa(L,1)}(E)||Bi(),h.el=null,S){let F=x(u);for(;;){let L=r(u);if(L&&L!==F)l(L);else break}}let B=r(u),T=a(u);return l(u),i(null,h,T,B,g,_,pn(T),k),g&&(g.vnode.el=h.el,yr(g,h.el)),B},x=(u,h="[",g="]")=>{let _=0;for(;u;)if((u=r(u))&&Ui(u)&&(u.data===h&&_++,u.data===g)){if(_===0)return r(u);_--}return u},q=(u,h,g)=>{let _=h.parentNode;_&&_.replaceChild(u,h);let k=g;for(;k;)k.vnode.el===h&&(k.vnode.el=k.subTree.el=u),k=k.parent},b=u=>u.nodeType===1&&u.tagName==="TEMPLATE";return[(u,h)=>{if(!h.hasChildNodes()){i(null,u,h),Pn(),h._vnode=u;return}d(h.firstChild,u,null,null,null),Pn(),h._vnode=u},d]}var Ln="data-allow-mismatch",bu={0:"text",1:"children",2:"class",3:"style",4:"attribute"};function un(e,t){if(t===0||t===1)for(;e&&!e.hasAttribute(Ln);)e=e.parentElement;return sa(e&&e.getAttribute(Ln),t)}function sa(e,t){if(e==null)return!1;{if(e==="")return!0;let i=e.split(",");return!!(t===0&&i.includes("children"))||i.includes(bu[t])}}var yu=or().requestIdleCallback||(e=>setTimeout(e,1)),xu=or().cancelIdleCallback||(e=>clearTimeout(e)),wu=(e=1e4)=>t=>{let i=yu(t,{timeout:e});return()=>xu(i)},ku=e=>(t,i)=>{let s=new IntersectionObserver(n=>{for(let r of n)if(r.isIntersecting){s.disconnect(),t();break}},e);return i(n=>{if(n instanceof Element){if(function(r){let{top:a,left:l,bottom:o,right:c}=r.getBoundingClientRect(),{innerHeight:d,innerWidth:p}=window;return(a>0&&a<d||o>0&&o<d)&&(l>0&&l<p||c>0&&c<p)}(n))return t(),s.disconnect(),!1;s.observe(n)}}),()=>s.disconnect()},_u=e=>t=>{if(e){let i=matchMedia(e);if(!i.matches)return i.addEventListener("change",t,{once:!0}),()=>i.removeEventListener("change",t);t()}},Su=(e=[])=>(t,i)=>{re(e)&&(e=[e]);let s=!1,n=a=>{s||(s=!0,r(),t(),a.target.dispatchEvent(new a.constructor(a.type,a)))},r=()=>{i(a=>{for(let l of e)a.removeEventListener(l,n)})};return i(a=>{for(let l of e)a.addEventListener(l,n,{once:!0})}),r},Kt=e=>!!e.type.__asyncLoader;function qu(e){let t;se(e)&&(e={loader:e});let{loader:i,loadingComponent:s,errorComponent:n,delay:r=200,hydrate:a,timeout:l,suspensible:o=!0,onError:c}=e,d=null,p=0,f=()=>{let y;return d||(y=d=i().catch(m=>{if(m=m instanceof Error?m:Error(String(m)),c)return new Promise((x,q)=>{c(m,()=>x((p++,d=null,f())),()=>q(m),p+1)});throw m}).then(m=>y!==d&&d?d:(m&&(m.__esModule||m[Symbol.toStringTag]==="Module")&&(m=m.default),t=m,m)))};return Fa({name:"AsyncComponentWrapper",__asyncLoader:f,__asyncHydrate(y,m,x){let q=y.isConnected,b=!1;(m.bu||(m.bu=[])).push(()=>b=!0);let u=()=>{b||y.parentNode&&(!q||y.isConnected)&&x()},h=a?()=>{let g=a(u,_=>function(k,S){if(Ui(k)&&k.data==="["){let C=1,E=k.nextSibling;for(;E;){if(E.nodeType===1){if(S(E)===!1)break}else if(Ui(E))if(E.data==="]"){if(--C==0)break}else E.data==="["&&C++;E=E.nextSibling}}else S(k)}(y,_));g&&(m.bum||(m.bum=[])).push(g)}:u;t?h():f().then(()=>!m.isUnmounted&&h())},get __asyncResolved(){return t},setup(){let y,m,x=Ke;if(za(x),t)return()=>hn(t,x);let q=g=>{d=null,ji(g,x,13,!n)};if(o&&x.suspense||Ii)return f().then(g=>()=>hn(g,x)).catch(g=>(q(g),()=>n?Te(n,{error:g}):null));let b=qs(!1),u=qs(),h=qs(!!r);return Ys(()=>{y!=null&&clearTimeout(y),m!=null&&clearTimeout(m)}),r&&(m=setTimeout(()=>{x.isUnmounted||(h.value=!1)},r)),l!=null&&(y=setTimeout(()=>{if(!x.isUnmounted&&!b.value&&!u.value){let g=Error(`Async component timed out after ${l}ms.`);q(g),u.value=g}},l)),f().then(()=>{!x.isUnmounted&&(b.value=!0,x.parent&&Js(x.parent.vnode)&&x.parent.update())}).catch(g=>{if(x.isUnmounted){d=null;return}q(g),u.value=g}),()=>b.value&&t?hn(t,x):u.value&&n?Te(n,{error:u.value}):s&&!h.value?hn(s,x):void 0}})}function hn(e,t){let{ref:i,props:s,children:n,ce:r}=t.vnode,a=Te(e,s,n);return a.ref=i,a.ce=r,delete t.vnode.ce,a}var Js=e=>e.type.__isKeepAlive,Tu={name:"KeepAlive",__isKeepAlive:!0,props:{include:[String,RegExp,Array],exclude:[String,RegExp,Array],max:[String,Number]},setup(e,{slots:t}){let i=rt(),s=i.ctx;if(!s.renderer)return()=>{let u=t.default&&t.default();return u&&u.length===1?u[0]:u};let n=new Map,r=new Set,a=null,l=i.suspense,{renderer:{p:o,m:c,um:d,o:{createElement:p}}}=s,f=p("div");function y(u){zr(u),d(u,i,l,!0)}function m(u){n.forEach((h,g)=>{let _=ha(Kt(h)?h.type.__asyncResolved||{}:h.type);_&&!u(_)&&x(g)})}function x(u){let h=n.get(u);!h||a&&Tt(h,a)?a&&zr(a):y(h),n.delete(u),r.delete(u)}s.activate=(u,h,g,_,k)=>{let S=u.component;c(u,h,g,0,l),o(S.vnode,u,h,g,S,l,_,u.slotScopeIds,k),Pe(()=>{S.isDeactivated=!1,S.a&&Ji(S.a);let C=u.props&&u.props.onVnodeMounted;C&&ot(C,S.parent,u)},l)},s.deactivate=u=>{let h=u.component;Dn(h.m),Dn(h.a),c(u,f,null,1,l),Pe(()=>{h.da&&Ji(h.da);let g=u.props&&u.props.onVnodeUnmounted;g&&ot(g,h.parent,u),h.isDeactivated=!0},l)},Zi(()=>[e.include,e.exclude],([u,h])=>{u&&m(g=>xs(u,g)),h&&m(g=>!xs(h,g))},{flush:"post",deep:!0});let q=null,b=()=>{q!=null&&($n(i.subTree.type)?Pe(()=>{n.set(q,mn(i.subTree))},i.subTree.suspense):n.set(q,mn(i.subTree)))};return Gs(b),gr(b),br(()=>{n.forEach(u=>{let{subTree:h,suspense:g}=i,_=mn(h);if(u.type===_.type&&u.key===_.key){zr(_);let k=_.component.da;k&&Pe(k,g);return}y(u)})}),()=>{if(q=null,!t.default)return a=null;let u=t.default(),h=u[0];if(u.length>1)return a=null,u;if(!Zt(h)||!(4&h.shapeFlag)&&!(128&h.shapeFlag))return a=null,h;let g=mn(h);if(g.type===Re)return a=null,g;let _=g.type,k=ha(Kt(g)?g.type.__asyncResolved||{}:_),{include:S,exclude:C,max:E}=e;if(S&&(!k||!xs(S,k))||C&&k&&xs(C,k))return g.shapeFlag&=-257,a=g,h;let O=g.key==null?_:g.key,B=n.get(O);return g.el&&(g=jt(g),128&h.shapeFlag&&(h.ssContent=g)),q=O,B?(g.el=B.el,g.component=B.component,g.transition&&Xt(g,g.transition),g.shapeFlag|=512,r.delete(O),r.add(O)):(r.add(O),E&&r.size>parseInt(E,10)&&x(r.values().next().value)),g.shapeFlag|=256,a=g,$n(h.type)?h:g}}};function xs(e,t){let i;return G(e)?e.some(s=>xs(s,t)):re(e)?e.split(",").includes(t):(i=e,Me.call(i)==="[object RegExp]"&&(e.lastIndex=0,e.test(t)))}function oc(e,t){dc(e,"a",t)}function cc(e,t){dc(e,"da",t)}function dc(e,t,i=Ke){let s=e.__wdc||(e.__wdc=()=>{let n=i;for(;n;){if(n.isDeactivated)return;n=n.parent}return e()});if(Fn(t,s,i),i){let n=i.parent;for(;n&&n.parent;)Js(n.parent.vnode)&&function(r,a,l,o){let c=Fn(a,r,o,!0);Ys(()=>{Aa(o[a],c)},l)}(s,t,i,n),n=n.parent}}function zr(e){e.shapeFlag&=-257,e.shapeFlag&=-513}function mn(e){return 128&e.shapeFlag?e.ssContent:e}function Fn(e,t,i=Ke,s=!1){if(i){let n=i[e]||(i[e]=[]),r=t.__weh||(t.__weh=(...a)=>{Gt();let l=os(i),o=vt(t,i,e,a);return l(),Yt(),o});return s?n.unshift(r):n.push(r),r}}var ei=e=>(t,i=Ke)=>{Ii&&e!=="sp"||Fn(e,(...s)=>t(...s),i)},pc=ei("bm"),Gs=ei("m"),Ba=ei("bu"),gr=ei("u"),br=ei("bum"),Ys=ei("um"),uc=ei("sp"),hc=ei("rtg"),mc=ei("rtc");function fc(e,t=Ke){Fn("ec",e,t)}var Da="components";function Cu(e,t){return $a(Da,e,!0,t)||e}var vc=Symbol.for("v-ndc");function Mu(e){return re(e)?$a(Da,e,!1)||e:e||vc}function Au(e){return $a("directives",e)}function $a(e,t,i=!0,s=!1){let n=Qe||Ke;if(n){let r=n.type;if(e===Da){let l=ha(r,!1);if(l&&(l===t||l===ye(t)||l===Pi(ye(t))))return r}let a=Cl(n[e]||r[e],t)||Cl(n.appContext[e],t);return!a&&s?r:a}}function Cl(e,t){return e&&(e[t]||e[ye(t)]||e[Pi(ye(t))])}function Iu(e,t,i,s){let n,r=i&&i[s],a=G(e);if(a||re(e)){let l=a&&Ht(e),o=!1,c=!1;l&&(o=!ut(e),c=Pt(e),e=pr(e)),n=Array(e.length);for(let d=0,p=e.length;d<p;d++)n[d]=t(o?c?Yi(Mt(e[d])):Mt(e[d]):e[d],d,void 0,r&&r[d])}else if(typeof e=="number"){n=Array(e);for(let l=0;l<e;l++)n[l]=t(l+1,l,void 0,r&&r[l])}else if(me(e))if(e[Symbol.iterator])n=Array.from(e,(l,o)=>t(l,o,void 0,r&&r[o]));else{let l=Object.keys(e);n=Array(l.length);for(let o=0,c=l.length;o<c;o++){let d=l[o];n[o]=t(e[d],d,o,r&&r[o])}}else n=[];return i&&(i[s]=n),n}function Nu(e,t){for(let i=0;i<t.length;i++){let s=t[i];if(G(s))for(let n=0;n<s.length;n++)e[s[n].name]=s[n].fn;else s&&(e[s.name]=s.key?(...n)=>{let r=s.fn(...n);return r&&(r.key=s.key),r}:s.fn)}return e}function Eu(e,t,i={},s,n,r){let a;if(Qe.ce||Qe.parent&&Kt(Qe.parent)&&Qe.parent.ce){let c=r!=null&&i.key==null?de({},i,{key:r}):i,d=Object.keys(c).length>0;return t!=="default"&&(c.name=t),Ls(),Un($e,null,[Te("slot",c,s&&s())],d?-2:64)}let l=e[t];l&&l._c&&(l._d=!1);let o=Qt.length;Ls();try{let c=l&&Ua(l(i)),d=i.key||r||c&&c.key;a=Un($e,{key:(d&&!Ze(d)?d:`_${t}`)+(!c&&s?"_fb":"")},c||(s?s():[]),c&&e._===1?64:-2)}catch(c){for(let d=Qt.length;d>o;d--)xr();throw c}finally{l&&l._c&&(l._d=!0)}return!n&&a.scopeId&&(a.slotScopeIds=[a.scopeId+"-s"]),a}function Ua(e){return e.some(t=>!Zt(t)||t.type!==Re&&(t.type!==$e||!!Ua(t.children)))?e:null}function Ou(e,t){let i={};for(let s in e)i[t&&/[A-Z]/.test(s)?`on:${s}`:Wi(s)]=e[s];return i}var na=e=>e?jc(e)?Xs(e):na(e.parent):null,Ms=de(Object.create(null),{$:e=>e,$el:e=>e.vnode.el,$data:e=>e.data,$props:e=>e.props,$attrs:e=>e.attrs,$slots:e=>e.slots,$refs:e=>e.refs,$parent:e=>na(e.parent),$root:e=>na(e.root),$host:e=>e.ce,$emit:e=>e.emit,$options:e=>la(e),$forceUpdate:e=>e.f||(e.f=()=>{Ra(e.update)}),$nextTick:e=>e.n||(e.n=mr.bind(e.proxy)),$watch:e=>hu.bind(e)}),Br=(e,t)=>e!==pe&&!e.__isScriptSetup&&fe(e,t),ra={get({_:e},t){let i,s;if(t==="__v_skip")return!0;let{ctx:n,setupState:r,data:a,props:l,accessCache:o,type:c,appContext:d}=e;if(t[0]!=="$"){let f=o[t];if(f!==void 0)switch(f){case 1:return r[t];case 2:return a[t];case 4:return n[t];case 3:return l[t]}else{if(Br(r,t))return o[t]=1,r[t];if(a!==pe&&fe(a,t))return o[t]=2,a[t];if(fe(l,t))return o[t]=3,l[t];if(n!==pe&&fe(n,t))return o[t]=4,n[t];aa&&(o[t]=0)}}let p=Ms[t];return p?(t==="$attrs"&&Ye(e.attrs,"get",""),p(e)):(i=c.__cssModules)&&(i=i[t])?i:n!==pe&&fe(n,t)?(o[t]=4,n[t]):fe(s=d.config.globalProperties,t)?s[t]:void 0},set({_:e},t,i){let{data:s,setupState:n,ctx:r}=e;return Br(n,t)?(n[t]=i,!0):s!==pe&&fe(s,t)?(s[t]=i,!0):!fe(e.props,t)&&!(t[0]==="$"&&t.slice(1)in e)&&(r[t]=i,!0)},has({_:{data:e,setupState:t,accessCache:i,ctx:s,appContext:n,props:r,type:a}},l){let o;return!!(i[l]||e!==pe&&l[0]!=="$"&&fe(e,l)||Br(t,l)||fe(r,l)||fe(s,l)||fe(Ms,l)||fe(n.config.globalProperties,l)||(o=a.__cssModules)&&o[l])},defineProperty(e,t,i){return i.get!=null?e._.accessCache[t]=0:fe(i,"value")&&this.set(e,t,i.value,null),Reflect.defineProperty(e,t,i)}},Ru=de({},ra,{get(e,t){if(t!==Symbol.unscopables)return ra.get(e,t,e)},has:(e,t)=>t[0]!=="_"&&!_p(t)});function Pu(){return null}function ju(){return null}function Lu(e){}function Fu(e){}function zu(){return null}function Bu(){}function Du(e,t){return null}function $u(){return gc().slots}function Uu(){return gc().attrs}function gc(e){let t=rt();return t.setupContext||(t.setupContext=Bc(t))}function js(e){return G(e)?e.reduce((t,i)=>(t[i]=null,t),{}):e}function Vu(e,t){let i=js(e);for(let s in t){if(s.startsWith("__skip"))continue;let n=i[s];n?G(n)||se(n)?n=i[s]={type:n,default:t[s]}:n.default=t[s]:n===null&&(n=i[s]={default:t[s]}),n&&t[`__skip_${s}`]&&(n.skipFactory=!0)}return i}function Hu(e,t){return e&&t?G(e)&&G(t)?e.concat(t):de({},js(e),js(t)):e||t}function Ku(e,t){let i={};for(let s in e)t.includes(s)||Object.defineProperty(i,s,{enumerable:!0,get:()=>e[s]});return i}function Qu(e){let t=rt(),i=Ii,s=e();zs(),i&&Ki(!1);let n=()=>{os(t),i&&Ki(!0)},r=()=>{rt()!==t&&t.scope.off(),zs(),i&&Ki(!1)};return Ia(s)&&(s=s.catch(a=>{throw n(),Promise.resolve().then(()=>Promise.resolve().then(r)),a})),[s,()=>{n(),Promise.resolve().then(r)}]}var aa=!0;function Ml(e,t,i){vt(G(e)?e.map(s=>s.bind(t.proxy)):e.bind(t.proxy),t,i)}function la(e){let t,i=e.type,{mixins:s,extends:n}=i,{mixins:r,optionsCache:a,config:{optionMergeStrategies:l}}=e.appContext,o=a.get(i);return o?t=o:r.length||s||n?(t={},r.length&&r.forEach(c=>zn(t,c,l,!0)),zn(t,i,l)):t=i,me(i)&&a.set(i,t),t}function zn(e,t,i,s=!1){let{mixins:n,extends:r}=t;for(let a in r&&zn(e,r,i,!0),n&&n.forEach(l=>zn(e,l,i,!0)),t)if(!(s&&a==="expose")){let l=Wu[a]||i&&i[a];e[a]=l?l(e[a],t[a]):t[a]}return e}var Wu={data:Al,props:Il,emits:Il,methods:gs,computed:gs,beforeCreate:it,created:it,beforeMount:it,mounted:it,beforeUpdate:it,updated:it,beforeDestroy:it,beforeUnmount:it,destroyed:it,unmounted:it,activated:it,deactivated:it,errorCaptured:it,serverPrefetch:it,components:gs,directives:gs,watch:function(e,t){if(!e)return t;if(!t)return e;let i=de(Object.create(null),e);for(let s in t)i[s]=it(e[s],t[s]);return i},provide:Al,inject:function(e,t){return gs(oa(e),oa(t))}};function Al(e,t){return t?e?function(){return de(se(e)?e.call(this,this):e,se(t)?t.call(this,this):t)}:t:e}function oa(e){if(G(e)){let t={};for(let i=0;i<e.length;i++)t[e[i]]=e[i];return t}return e}function it(e,t){return e?[...new Set([].concat(e,t))]:t}function gs(e,t){return e?de(Object.create(null),e,t):t}function Il(e,t){return e?G(e)&&G(t)?[...new Set([...e,...t])]:de(Object.create(null),js(e),js(t??{})):t}function bc(){return{app:null,config:{isNativeTag:$i,performance:!1,globalProperties:{},optionMergeStrategies:{},errorHandler:void 0,warnHandler:void 0,compilerOptions:{}},mixins:[],components:{},directives:{},provides:Object.create(null),optionsCache:new WeakMap,propsCache:new WeakMap,emitsCache:new WeakMap}}var Ju=0,qi=null;function Gu(e,t,i=pe){let s=rt(),n=ye(t),r=dt(t),a=yc(e,n),l=Wo((o,c)=>{let d,p,f=pe;return tc(()=>{let y=e[n];De(d,y)&&(d=y,c())}),{get:()=>(o(),i.get?i.get(d):d),set(y){let m=i.set?i.set(y):y;if(!De(m,d)&&!(f!==pe&&De(y,f)))return;let x=s.vnode.props,q=!!(x&&(t in x||n in x||r in x)&&(`onUpdate:${t}`in x||`onUpdate:${n}`in x||`onUpdate:${r}`in x));q||(d=y,c()),s.emit(`update:${t}`,m),De(y,f)&&(De(y,m)&&!De(m,p)||q&&f!==pe&&!De(m,d))&&c(),f=y,p=m}}});return l[Symbol.iterator]=()=>{let o=0;return{next:()=>o<2?{value:o++?a||pe:l,done:!1}:{done:!0}}},l}var yc=(e,t)=>t==="modelValue"||t==="model-value"?e.modelModifiers:e[`${t}Modifiers`]||e[`${ye(t)}Modifiers`]||e[`${dt(t)}Modifiers`];function Yu(e,t,...i){let s;if(e.isUnmounted)return;let n=e.vnode.props||pe,r=i,a=t.startsWith("update:"),l=a&&yc(n,t.slice(7));l&&(l.trim&&(r=i.map(d=>re(d)?d.trim():d)),l.number&&(r=i.map(lr)));let o=n[s=Wi(t)]||n[s=Wi(ye(t))];!o&&a&&(o=n[s=Wi(dt(t))]),o&&vt(o,e,6,r);let c=n[s+"Once"];if(c){if(e.emitted){if(e.emitted[s])return}else e.emitted={};e.emitted[s]=!0,vt(c,e,6,r)}}var Xu=new WeakMap;function Bn(e,t){return!!e&&!!Ri(t)&&(fe(e,(t=(t=t.slice(2))==="Once"?t:t.replace(/Once$/,""))[0].toLowerCase()+t.slice(1))||fe(e,dt(t))||fe(e,t))}function _n(e){let t,i,{type:s,vnode:n,proxy:r,withProxy:a,propsOptions:[l],slots:o,attrs:c,emit:d,render:p,renderCache:f,props:y,data:m,setupState:x,ctx:q,inheritAttrs:b}=e,u=Ps(e);try{if(4&n.shapeFlag){let g=a||r;t=ct(p.call(g,g,f,y,x,m,q)),i=c}else t=ct(s.length>1?s(y,{attrs:c,slots:o,emit:d}):s(y,null)),i=s.props?c:Zu(c)}catch(g){Qt.length=0,ji(g,e,1),t=Te(Re)}let h=t;if(i&&b!==!1){let g=Object.keys(i),{shapeFlag:_}=h;g.length&&7&_&&(l&&g.some(nr)&&(i=eh(i,l)),h=jt(h,i,!1,!0))}return n.dirs&&((h=jt(h,null,!1,!0)).dirs=h.dirs?h.dirs.concat(n.dirs):n.dirs),n.transition&&Xt(h,n.transition),t=h,Ps(u),t}var Zu=e=>{let t;for(let i in e)(i==="class"||i==="style"||Ri(i))&&((t||(t={}))[i]=e[i]);return t},eh=(e,t)=>{let i={};for(let s in e)nr(s)&&s.slice(9)in t||(i[s]=e[s]);return i};function Nl(e,t,i){let s=Object.keys(t);if(s.length!==Object.keys(e).length)return!0;for(let n=0;n<s.length;n++){let r=s[n];if(xc(t,e,r)&&!Bn(i,r))return!0}return!1}function xc(e,t,i){let s=e[i],n=t[i];return i==="style"&&me(s)&&me(n)?!Jt(s,n):s!==n}function yr({vnode:e,parent:t,suspense:i},s){for(;t;){let n=t.subTree;if(n.suspense&&n.suspense.activeBranch===e&&(n.suspense.vnode.el=n.el=s,e=n),n===e)(e=t.vnode).el=s,t=t.parent;else break}i&&i.activeBranch===e&&(i.vnode.el=s)}var ca={},wc=e=>Object.getPrototypeOf(e)===ca;function kc(e,t,i,s){let n,[r,a]=e.propsOptions,l=!1;if(t)for(let o in t){let c;if(Vt(o))continue;let d=t[o];r&&fe(r,c=ye(o))?a&&a.includes(c)?(n||(n={}))[c]=d:i[c]=d:Bn(e.emitsOptions,o)||o in s&&d===s[o]||(s[o]=d,l=!0)}if(a){let o=ue(i),c=n||pe;for(let d=0;d<a.length;d++){let p=a[d];i[p]=da(r,o,p,c[p],e,!fe(c,p))}}return l}function da(e,t,i,s,n,r){let a=e[i];if(a!=null){let l=fe(a,"default");if(l&&s===void 0){let o=a.default;if(a.type!==Function&&!a.skipFactory&&se(o)){let{propsDefaults:c}=n;if(i in c)s=c[i];else{let d=os(n);s=c[i]=o.call(null,t),d()}}else s=o;n.ce&&n.ce._setProp(i,s)}a[0]&&(r&&!l?s=!1:a[1]&&(s===""||s===dt(i))&&(s=!0))}return s}var th=new WeakMap;function El(e){return!(e[0]==="$"||Vt(e))}var Va=e=>e==="_"||e==="_ctx"||e==="$stable",Ha=e=>G(e)?e.map(ct):[ct(e)],ih=(e,t,i)=>{if(t._n)return t;let s=Pa((...n)=>Ha(t(...n)),i);return s._c=!1,s},_c=(e,t,i)=>{let s=e._ctx;for(let n in e){if(Va(n))continue;let r=e[n];if(se(r))t[n]=ih(n,r,s);else if(r!=null){let a=Ha(r);t[n]=()=>a}}},Sc=(e,t)=>{let i=Ha(t);e.slots.default=()=>i},qc=(e,t,i)=>{for(let s in t)(i||!Va(s))&&(e[s]=t[s])},Pe=Ac;function Ka(e){return Cc(e)}function Tc(e){return Cc(e,gu)}function Cc(e,t){var i;let s,n;or().__VUE__=!0;let{insert:r,remove:a,patchProp:l,createElement:o,createText:c,createComment:d,setText:p,setElementText:f,parentNode:y,nextSibling:m,setScopeId:x=He,insertStaticContent:q}=e,b=(v,w,A,$=null,P=null,I=null,z,R=null,j=!!w.dynamicChildren)=>{if(v===w)return;v&&!Tt(v,w)&&($=ce(v),he(v,P,I,!0),v=null),w.patchFlag===-2&&(j=!1,w.dynamicChildren=null);let{type:N,ref:U,shapeFlag:H}=w;switch(N){case oi:u(v,w,A,$);break;case Re:h(v,w,A,$);break;case Ti:v==null&&g(w,A,$,z);break;case $e:T(v,w,A,$,P,I,z,R,j);break;default:1&H?_(v,w,A,$,P,I,z,R,j):6&H?F(v,w,A,$,P,I,z,R,j):(64&H||128&H)&&N.process(v,w,A,$,P,I,z,R,j,Se)}U!=null&&P?es(U,v&&v.ref,I,w||v,!w):U==null&&v&&v.ref!=null&&es(v.ref,null,I,v,!0)},u=(v,w,A,$)=>{if(v==null)r(w.el=c(w.children),A,$);else{let P=w.el=v.el;w.children!==v.children&&p(P,w.children)}},h=(v,w,A,$)=>{v==null?r(w.el=d(w.children||""),A,$):w.el=v.el},g=(v,w,A,$)=>{[v.el,v.anchor]=q(v.children,w,A,$,v.el,v.anchor)},_=(v,w,A,$,P,I,z,R,j)=>{if(w.type==="svg"?z="svg":w.type==="math"&&(z="mathml"),v==null)k(w,A,$,P,I,z,R,j);else{let N=v.el&&v.el._isVueCE?v.el:null;try{N&&N._beginPatch(),E(v,w,P,I,z,R,j)}finally{N&&N._endPatch()}}},k=(v,w,A,$,P,I,z,R)=>{let j,N,{props:U,shapeFlag:H,transition:ee,dirs:X}=v;if(j=v.el=o(v.type,I,U&&U.is,U),8&H?f(j,v.children):16&H&&C(v.children,j,null,$,P,Dr(v,I),z,R),X&&Ot(v,null,$,"created"),S(j,v,v.scopeId,z,$),U){for(let ie in U)ie==="value"||Vt(ie)||l(j,ie,null,U[ie],I,$);"value"in U&&l(j,"value",null,U.value,I),(N=U.onVnodeBeforeMount)&&ot(N,$,v)}X&&Ot(v,null,$,"beforeMount");let le=Mc(P,ee);le&&ee.beforeEnter(j),r(j,w,A),((N=U&&U.onVnodeMounted)||le||X)&&Pe(()=>{N&&ot(N,$,v),le&&ee.enter(j),X&&Ot(v,null,$,"mounted")},P)},S=(v,w,A,$,P)=>{if(A&&x(v,A),$)for(let I=0;I<$.length;I++)x(v,$[I]);if(P){let I=P.subTree;if(w===I||$n(I.type)&&(I.ssContent===w||I.ssFallback===w)){let z=P.vnode;S(v,z,z.scopeId,z.slotScopeIds,P.parent)}}},C=(v,w,A,$,P,I,z,R,j=0)=>{for(let N=j;N<v.length;N++)b(null,v[N]=R?Bt(v[N]):ct(v[N]),w,A,$,P,I,z,R)},E=(v,w,A,$,P,I,z)=>{let R,j=w.el=v.el,{patchFlag:N,dynamicChildren:U,dirs:H}=w;N|=16&v.patchFlag;let ee=v.props||pe,X=w.props||pe;if(A&&gi(A,!1),(R=X.onVnodeBeforeUpdate)&&ot(R,A,w,v),H&&Ot(w,v,A,"beforeUpdate"),A&&gi(A,!0),U&&(!v.dynamicChildren||v.dynamicChildren.length!==U.length)&&(N=0,z=!1,U=null),(ee.innerHTML&&X.innerHTML==null||ee.textContent&&X.textContent==null)&&f(j,""),U?O(v.dynamicChildren,U,j,A,$,Dr(w,P),I):z||J(v,w,j,null,A,$,Dr(w,P),I,!1),N>0){if(16&N)B(j,ee,X,A,P);else if(2&N&&ee.class!==X.class&&l(j,"class",null,X.class,P),4&N&&l(j,"style",ee.style,X.style,P),8&N){let le=w.dynamicProps;for(let ie=0;ie<le.length;ie++){let ge=le[ie],Ce=ee[ge],Ie=X[ge];(Ie!==Ce||ge==="value")&&l(j,ge,Ce,Ie,P,A)}}1&N&&v.children!==w.children&&f(j,w.children)}else z||U!=null||B(j,ee,X,A,P);((R=X.onVnodeUpdated)||H)&&Pe(()=>{R&&ot(R,A,w,v),H&&Ot(w,v,A,"updated")},$)},O=(v,w,A,$,P,I,z)=>{for(let R=0;R<w.length;R++){let j=v[R],N=w[R],U=j.el&&(j.type===$e||!Tt(j,N)||198&j.shapeFlag)?y(j.el):A;b(j,N,U,null,$,P,I,z,!0)}},B=(v,w,A,$,P)=>{if(w!==A){if(w!==pe)for(let I in w)Vt(I)||I in A||l(v,I,w[I],null,P,$);for(let I in A){if(Vt(I))continue;let z=A[I],R=w[I];z!==R&&I!=="value"&&l(v,I,R,z,P,$)}"value"in A&&l(v,"value",w.value,A.value,P)}},T=(v,w,A,$,P,I,z,R,j)=>{let N=w.el=v?v.el:c(""),U=w.anchor=v?v.anchor:c(""),{patchFlag:H,dynamicChildren:ee,slotScopeIds:X}=w;X&&(R=R?R.concat(X):X),v==null?(r(N,A,$),r(U,A,$),C(w.children||[],A,U,P,I,z,R,j)):H>0&&64&H&&ee&&v.dynamicChildren&&v.dynamicChildren.length===ee.length?(O(v.dynamicChildren,ee,A,P,I,z,R),(w.key!=null||P&&w===P.subTree)&&Qa(v,w,!0)):J(v,w,A,U,P,I,z,R,j)},F=(v,w,A,$,P,I,z,R,j)=>{w.slotScopeIds=R,v==null?512&w.shapeFlag?P.ctx.activate(w,A,$,z,j):L(w,A,$,P,I,z,j):M(v,w,j)},L=(v,w,A,$,P,I,z)=>{let R=v.component=Pc(v,$,P);if(Js(v)&&(R.ctx.renderer=Se),Lc(R,!1,z),R.asyncDep){if(P&&P.registerDep(R,Q,z),!v.el){let j=R.subTree=Te(Re);h(null,j,w,A),v.placeholder=j.el}}else Q(R,v,w,A,P,I,z)},M=(v,w,A)=>{let $=w.component=v.component;if(function(P,I,z){let{props:R,children:j,component:N}=P,{props:U,children:H,patchFlag:ee}=I,X=N.emitsOptions;if(I.dirs||I.transition)return!0;if(!z||!(ee>=0))return(!!j||!!H)&&(!H||!H.$stable)||R!==U&&(R?!U||Nl(R,U,X):!!U);if(1024&ee)return!0;if(16&ee)return R?Nl(R,U,X):!!U;if(8&ee){let le=I.dynamicProps;for(let ie=0;ie<le.length;ie++){let ge=le[ie];if(xc(U,R,ge)&&!Bn(X,ge))return!0}}return!1}(v,w,A)){if($.asyncDep&&!$.asyncResolved)return void V($,w,A);$.next=w,$.update()}else w.el=v.el,$.vnode=w},Q=(v,w,A,$,P,I,z)=>{v.scope.on();let R=v.effect=new Mi(()=>{if(v.isMounted){let U,{next:H,bu:ee,u:X,parent:le,vnode:ie}=v;{let lt=function an(fi){let ti=fi.subTree.component;if(ti)return ti.asyncDep&&!ti.asyncResolved?ti:an(ti)}(v);if(lt){H&&(H.el=ie.el,V(v,H,z)),lt.asyncDep.then(()=>{Pe(()=>{v.isUnmounted||j()},P)});return}}let ge=H;gi(v,!1),H?(H.el=ie.el,V(v,H,z)):H=ie,ee&&Ji(ee),(U=H.props&&H.props.onVnodeBeforeUpdate)&&ot(U,le,H,ie),gi(v,!0);let Ce=_n(v),Ie=v.subTree;v.subTree=Ce,b(Ie,Ce,y(Ie.el),ce(Ie),v,P,I),H.el=Ce.el,ge===null&&yr(v,Ce.el),X&&Pe(X,P),(U=H.props&&H.props.onVnodeUpdated)&&Pe(()=>ot(U,le,H,ie),P)}else{let U,{el:H,props:ee}=w,{bm:X,m:le,parent:ie,root:ge,type:Ce}=v,Ie=Kt(w);if(gi(v,!1),X&&Ji(X),!Ie&&(U=ee&&ee.onVnodeBeforeMount)&&ot(U,ie,w),gi(v,!0),H&&n){let lt=()=>{v.subTree=_n(v),n(H,v.subTree,v,P,null)};Ie&&Ce.__asyncHydrate?Ce.__asyncHydrate(H,v,lt):lt()}else{ge.ce&&ge.ce._hasShadowRoot()&&ge.ce._injectChildStyle(Ce,v.parent?v.parent.type:void 0);let lt=v.subTree=_n(v);b(null,lt,A,$,v,P,I),w.el=lt.el}if(le&&Pe(le,P),!Ie&&(U=ee&&ee.onVnodeMounted)){let lt=w;Pe(()=>ot(U,ie,lt),P)}(256&w.shapeFlag||ie&&Kt(ie.vnode)&&256&ie.vnode.shapeFlag)&&v.a&&Pe(v.a,P),v.isMounted=!0,w=A=$=null}});v.scope.off();let j=v.update=R.run.bind(R),N=v.job=R.runIfDirty.bind(R);N.i=v,N.id=v.uid,R.scheduler=()=>Ra(N),gi(v,!0),j()},V=(v,w,A)=>{w.component=v;let $=v.vnode.props;v.vnode=w,v.next=null,function(P,I,z,R){let{props:j,attrs:N,vnode:{patchFlag:U}}=P,H=ue(j),[ee]=P.propsOptions,X=!1;if((R||U>0)&&!(16&U)){if(8&U){let le=P.vnode.dynamicProps;for(let ie=0;ie<le.length;ie++){let ge=le[ie];if(Bn(P.emitsOptions,ge))continue;let Ce=I[ge];if(ee)if(fe(N,ge))Ce!==N[ge]&&(N[ge]=Ce,X=!0);else{let Ie=ye(ge);j[Ie]=da(ee,H,Ie,Ce,P,!1)}else Ce!==N[ge]&&(N[ge]=Ce,X=!0)}}}else{let le;for(let ie in kc(P,I,j,N)&&(X=!0),H)I&&(fe(I,ie)||(le=dt(ie))!==ie&&fe(I,le))||(ee?z&&(z[ie]!==void 0||z[le]!==void 0)&&(j[ie]=da(ee,H,ie,void 0,P,!0)):delete j[ie]);if(N!==H)for(let ie in N)I&&fe(I,ie)||(delete N[ie],X=!0)}X&&Dt(P.attrs,"set","")}(v,w.props,$,A),((P,I,z)=>{let{vnode:R,slots:j}=P,N=!0,U=pe;if(32&R.shapeFlag){let H=I._;H?z&&H===1?N=!1:qc(j,I,z):(N=!I.$stable,_c(I,j)),U=I}else I&&(Sc(P,I),U={default:1});if(N)for(let H in j)Va(H)||U[H]!=null||delete j[H]})(v,w.children,A),Gt(),xl(v),Yt()},J=(v,w,A,$,P,I,z,R,j=!1)=>{let N=v&&v.children,U=v?v.shapeFlag:0,H=w.children,{patchFlag:ee,shapeFlag:X}=w;if(ee>0){if(128&ee)return void te(N,H,A,$,P,I,z,R,j);if(256&ee)return void K(N,H,A,$,P,I,z,R,j)}8&X?(16&U&&et(N,P,I),H!==N&&f(A,H)):16&U?16&X?te(N,H,A,$,P,I,z,R,j):et(N,P,I,!0):(8&U&&f(A,""),16&X&&C(H,A,$,P,I,z,R,j))},K=(v,w,A,$,P,I,z,R,j)=>{let N;v=v||Qi,w=w||Qi;let U=v.length,H=w.length,ee=Math.min(U,H);for(N=0;N<ee;N++){let X=w[N]=j?Bt(w[N]):ct(w[N]);b(v[N],X,A,null,P,I,z,R,j)}U>H?et(v,P,I,!0,!1,ee):C(w,A,$,P,I,z,R,j,ee)},te=(v,w,A,$,P,I,z,R,j)=>{let N=0,U=w.length,H=v.length-1,ee=U-1;for(;N<=H&&N<=ee;){let X=v[N],le=w[N]=j?Bt(w[N]):ct(w[N]);if(Tt(X,le))b(X,le,A,null,P,I,z,R,j);else break;N++}for(;N<=H&&N<=ee;){let X=v[H],le=w[ee]=j?Bt(w[ee]):ct(w[ee]);if(Tt(X,le))b(X,le,A,null,P,I,z,R,j);else break;H--,ee--}if(N>H){if(N<=ee){let X=ee+1,le=X<U?w[X].el:$;for(;N<=ee;)b(null,w[N]=j?Bt(w[N]):ct(w[N]),A,le,P,I,z,R,j),N++}}else if(N>ee)for(;N<=H;)he(v[N],P,I,!0),N++;else{let X,le=N,ie=N,ge=new Map;for(N=ie;N<=ee;N++){let Ne=w[N]=j?Bt(w[N]):ct(w[N]);Ne.key!=null&&ge.set(Ne.key,N)}let Ce=0,Ie=ee-ie+1,lt=!1,an=0,fi=Array(Ie);for(N=0;N<Ie;N++)fi[N]=0;for(N=le;N<=H;N++){let Ne,Be=v[N];if(Ce>=Ie){he(Be,P,I,!0);continue}if(Be.key!=null)Ne=ge.get(Be.key);else for(X=ie;X<=ee;X++)if(fi[X-ie]===0&&Tt(Be,w[X])){Ne=X;break}Ne===void 0?he(Be,P,I,!0):(fi[Ne-ie]=N+1,Ne>=an?an=Ne:lt=!0,b(Be,w[Ne],A,null,P,I,z,R,j),Ce++)}let ti=lt?function(Ne){let Be,hs,tt,It,vi,Li=Ne.slice(),xt=[0],bp=Ne.length;for(Be=0;Be<bp;Be++){let ln=Ne[Be];if(ln!==0){if(Ne[hs=xt[xt.length-1]]<ln){Li[Be]=hs,xt.push(Be);continue}for(tt=0,It=xt.length-1;tt<It;)Ne[xt[vi=tt+It>>1]]<ln?tt=vi+1:It=vi;ln<Ne[xt[tt]]&&(tt>0&&(Li[Be]=xt[tt-1]),xt[tt]=Be)}}for(tt=xt.length,It=xt[tt-1];tt-- >0;)xt[tt]=It,It=Li[It];return xt}(fi):Qi;for(X=ti.length-1,N=Ie-1;N>=0;N--){let Ne=ie+N,Be=w[Ne],hs=w[Ne+1],tt=Ne+1<U?hs.el||function It(vi){if(vi.placeholder)return vi.placeholder;let Li=vi.component;return Li?It(Li.subTree):null}(hs):$;fi[N]===0?b(null,Be,A,tt,P,I,z,R,j):lt&&(X<0||N!==ti[X]?ne(Be,A,tt,2):X--)}}},ne=(v,w,A,$,P=null)=>{let{el:I,type:z,transition:R,children:j,shapeFlag:N}=v;if(6&N)return void ne(v.component.subTree,w,A,$);if(128&N)return void v.suspense.move(w,A,$);if(64&N)return void z.move(v,w,A,Se);if(z===$e){r(I,w,A);for(let U=0;U<j.length;U++)ne(j[U],w,A,$);r(v.anchor,w,A);return}if(z===Ti)return void(({el:U,anchor:H},ee,X)=>{let le;for(;U&&U!==H;)le=m(U),r(U,ee,X),U=le;r(H,ee,X)})(v,w,A);if($!==2&&1&N&&R)if($===0)R.persisted&&!I[kt]?r(I,w,A):(R.beforeEnter(I),r(I,w,A),Pe(()=>R.enter(I),P));else{let{leave:U,delayLeave:H,afterLeave:ee}=R,X=()=>{v.ctx.isUnmounted?a(I):r(I,w,A)},le=()=>{let ie=I._isLeaving||!!I[kt];I._isLeaving&&I[kt](!0),R.persisted&&!ie?X():U(I,()=>{X(),ee&&ee()})};H?H(I,X,le):le()}else r(I,w,A)},he=(v,w,A,$=!1,P=!1)=>{let I,{type:z,props:R,ref:j,children:N,dynamicChildren:U,shapeFlag:H,patchFlag:ee,dirs:X,cacheIndex:le,memo:ie}=v;if(ee===-2&&(P=!1),j!=null&&(Gt(),es(j,null,A,v,!0),Yt()),le!=null&&(w.renderCache[le]=void 0),256&H)return void w.ctx.deactivate(v);let ge=1&H&&X,Ce=!Kt(v);if(Ce&&(I=R&&R.onVnodeBeforeUnmount)&&ot(I,w,v),6&H)Ve(v.component,A,$);else{if(128&H)return void v.suspense.unmount(A,$);ge&&Ot(v,null,w,"beforeUnmount"),64&H?v.type.remove(v,w,A,Se,$):U&&!U.hasOnce&&(z!==$e||ee>0&&64&ee)?et(U,w,A,!1,!0):(z===$e&&384&ee||!P&&16&H)&&et(N,w,A),$&&Ae(v)}let Ie=ie!=null&&le==null;(Ce&&(I=R&&R.onVnodeUnmounted)||ge||Ie)&&Pe(()=>{I&&ot(I,w,v),ge&&Ot(v,null,w,"unmounted"),Ie&&(v.el=null)},A)},Ae=v=>{let{type:w,el:A,anchor:$,transition:P}=v;if(w===$e)return void _e(A,$);if(w===Ti)return void(({el:z,anchor:R})=>{let j;for(;z&&z!==R;)j=m(z),a(z),z=j;a(R)})(v);let I=()=>{a(A),P&&!P.persisted&&P.afterLeave&&P.afterLeave()};if(1&v.shapeFlag&&P&&!P.persisted){let{leave:z,delayLeave:R}=P,j=()=>z(A,I);R?R(v.el,I,j):j()}else I()},_e=(v,w)=>{let A;for(;v!==w;)A=m(v),a(v),v=A;a(w)},Ve=(v,w,A)=>{let{bum:$,scope:P,job:I,subTree:z,um:R,m:j,a:N}=v;Dn(j),Dn(N),$&&Ji($),P.stop(),I&&(I.flags|=8,he(z,v,w,A)),R&&Pe(R,w),Pe(()=>{v.isUnmounted=!0},w)},et=(v,w,A,$=!1,P=!1,I=0)=>{for(let z=I;z<v.length;z++)he(v[z],w,A,$,P)},ce=v=>{if(6&v.shapeFlag)return ce(v.component.subTree);if(128&v.shapeFlag)return v.suspense.next();let w=m(v.anchor||v.el),A=w&&w[sc];return A?m(A):w},ae=!1,xe=(v,w,A)=>{let $;v==null?w._vnode&&(he(w._vnode,null,null,!0),$=w._vnode.component):b(w._vnode||null,v,w,null,null,null,A),w._vnode=v,ae||(ae=!0,xl($),Pn(),ae=!1)},Se={p:b,um:he,m:ne,r:Ae,mt:L,mc:C,pc:J,pbc:O,n:ce,o:e};return t&&([s,n]=t(Se)),{render:xe,hydrate:s,createApp:(i=s,function(v,w=null){se(v)||(v=de({},v)),w==null||me(w)||(w=null);let A=bc(),$=new WeakSet,P=[],I=!1,z=A.app={_uid:Ju++,_component:v,_props:w,_container:null,_context:A,_instance:null,version:Vc,get config(){return A.config},set config(R){},use:(R,...j)=>($.has(R)||(R&&se(R.install)?($.add(R),R.install(z,...j)):se(R)&&($.add(R),R(z,...j))),z),mixin:R=>(A.mixins.includes(R)||A.mixins.push(R),z),component:(R,j)=>j?(A.components[R]=j,z):A.components[R],directive:(R,j)=>j?(A.directives[R]=j,z):A.directives[R],mount(R,j,N){if(!I){let U=z._ceVNode||Te(v,w);return U.appContext=A,N===!0?N="svg":N===!1&&(N=void 0),j&&i?i(U,R):xe(U,R,N),I=!0,z._container=R,R.__vue_app__=z,Xs(U.component)}},onUnmount(R){P.push(R)},unmount(){I&&(vt(P,z._instance,16),xe(null,z._container),delete z._container.__vue_app__)},provide:(R,j)=>(A.provides[R]=j,z),runWithContext(R){let j=qi;qi=z;try{return R()}finally{qi=j}}};return z})}}function Dr({type:e,props:t},i){return i==="svg"&&e==="foreignObject"||i==="mathml"&&e==="annotation-xml"&&t&&t.encoding&&t.encoding.includes("html")?void 0:i}function gi({effect:e,job:t},i){i?(e.flags|=32,t.flags|=4):(e.flags&=-33,t.flags&=-5)}function Mc(e,t){return(!e||e&&!e.pendingBranch)&&t&&!t.persisted}function Qa(e,t,i=!1){let s=e.children,n=t.children;if(G(s)&&G(n))for(let r=0;r<s.length;r++){let a=s[r],l=n[r];1&l.shapeFlag&&!l.dynamicChildren&&((l.patchFlag<=0||l.patchFlag===32)&&((l=n[r]=Bt(n[r])).el=a.el),i||l.patchFlag===-2||Qa(a,l)),l.type===oi&&(l.patchFlag===-1&&(l=n[r]=Bt(l)),l.el=a.el),l.type!==Re||l.el||(l.el=a.el)}}function Dn(e){if(e)for(let t=0;t<e.length;t++)e[t].flags|=8}var $n=e=>e.__isSuspense,pa=0,sh={name:"Suspense",__isSuspense:!0,process(e,t,i,s,n,r,a,l,o,c){if(e==null)(function(d,p,f,y,m,x,q,b,u){let{p:h,o:{createElement:g}}=u,_=g("div"),k=d.suspense=Ol(d,m,y,p,_,f,x,q,b,u);h(null,k.pendingBranch=d.ssContent,_,null,y,k,x,q),k.deps>0?(As(d,"onPending"),As(d,"onFallback"),h(null,d.ssFallback,p,f,y,null,x,q),Vi(k,d.ssFallback)):k.resolve(!1,!0)})(t,i,s,n,r,a,l,o,c);else{if(r&&r.deps>0&&!e.suspense.isInFallback){t.suspense=e.suspense,t.suspense.vnode=t,t.el=e.el;return}(function(d,p,f,y,m,x,q,b,{p:u,um:h,o:{createElement:g}}){let _=p.suspense=d.suspense;_.vnode=p,p.el=d.el;let k=p.ssContent,S=p.ssFallback,{activeBranch:C,pendingBranch:E,isInFallback:O,isHydrating:B}=_;if(E)_.pendingBranch=k,Tt(E,k)?(u(E,k,_.hiddenContainer,null,m,_,x,q,b),_.deps<=0?_.resolve():O&&!B&&(u(C,S,f,y,m,null,x,q,b),Vi(_,S))):(_.pendingId=pa++,B?(_.isHydrating=!1,_.activeBranch=E):h(E,m,_),_.deps=0,_.effects.length=0,_.hiddenContainer=g("div"),O?(u(null,k,_.hiddenContainer,null,m,_,x,q,b),_.deps<=0?_.resolve():(u(C,S,f,y,m,null,x,q,b),Vi(_,S))):C&&Tt(C,k)?(u(C,k,f,y,m,_,x,q,b),_.resolve(!0)):(u(null,k,_.hiddenContainer,null,m,_,x,q,b),_.deps<=0&&_.resolve()));else if(C&&Tt(C,k))u(C,k,f,y,m,_,x,q,b),Vi(_,k);else if(As(p,"onPending"),_.pendingBranch=k,512&k.shapeFlag?_.pendingId=k.component.suspenseId:_.pendingId=pa++,u(null,k,_.hiddenContainer,null,m,_,x,q,b),_.deps<=0)_.resolve();else{let{timeout:T,pendingId:F}=_;T>0?setTimeout(()=>{_.pendingId===F&&_.fallback(S)},T):T===0&&_.fallback(S)}})(e,t,i,s,n,a,l,o,c)}},hydrate:function(e,t,i,s,n,r,a,l,o){let c=t.suspense=Ol(t,s,i,e.parentNode,document.createElement("div"),null,n,r,a,l,!0),d=o(e,c.pendingBranch=t.ssContent,i,c,r,a);return c.deps===0&&c.resolve(!1,!0),d},normalize:function(e){let{shapeFlag:t,children:i}=e,s=32&t;e.ssContent=Rl(s?i.default:i),e.ssFallback=s?Rl(i.fallback):Te(Re)}};function As(e,t){let i=e.props&&e.props[t];se(i)&&i()}function Ol(e,t,i,s,n,r,a,l,o,c,d=!1){var p;let f,y,{p:m,m:x,um:q,n:b,o:{parentNode:u,remove:h}}=c,g=(f=(p=e).props&&p.props.suspensible)!=null&&f!==!1;g&&t&&t.pendingBranch&&(y=t.pendingId,t.deps++);let _=e.props?Gi(e.props.timeout):void 0,k=r,S={vnode:e,parent:t,parentComponent:i,namespace:a,container:s,hiddenContainer:n,deps:0,pendingId:pa++,timeout:typeof _=="number"?_:-1,activeBranch:null,isFallbackMountPending:!1,pendingBranch:null,isInFallback:!d,isHydrating:d,isUnmounted:!1,effects:[],resolve(C=!1,E=!1){let{vnode:O,activeBranch:B,pendingBranch:T,pendingId:F,effects:L,parentComponent:M,container:Q,isInFallback:V}=S,J=!1;if(S.isHydrating)S.isHydrating=!1;else if(!C){J=B&&T.transition&&T.transition.mode==="out-in";let ne=!1;J&&(B.transition.afterLeave=()=>{F===S.pendingId&&(x(T,Q,r!==k||ne?r:b(B),0),Rs(L),V&&O.ssFallback&&(O.ssFallback.el=null))}),B&&!S.isFallbackMountPending&&(u(B.el)===Q&&(r=b(B),ne=!0),q(B,M,S,!0),!J&&V&&O.ssFallback&&Pe(()=>O.ssFallback.el=null,S)),J||x(T,Q,r,0)}S.isFallbackMountPending=!1,Vi(S,T),S.pendingBranch=null,S.isInFallback=!1;let K=S.parent,te=!1;for(;K;){if(K.pendingBranch){K.effects.push(...L),te=!0;break}K=K.parent}te||J||Rs(L),S.effects=[],g&&t&&t.pendingBranch&&y===t.pendingId&&(t.deps--,t.deps!==0||E||t.resolve()),As(O,"onResolve")},fallback(C){if(!S.pendingBranch)return;let{vnode:E,activeBranch:O,parentComponent:B,container:T,namespace:F}=S;As(E,"onFallback");let L=b(O),M=()=>{S.isFallbackMountPending=!1,S.isInFallback&&(m(null,C,T,L,B,null,F,l,o),Vi(S,C))},Q=C.transition&&C.transition.mode==="out-in";Q&&(S.isFallbackMountPending=!0,O.transition.afterLeave=M),S.isInFallback=!0,q(O,B,null,!0),Q||M()},move(C,E,O){S.activeBranch&&x(S.activeBranch,C,E,O),S.container=C},next:()=>S.activeBranch&&b(S.activeBranch),registerDep(C,E,O){let B=!!S.pendingBranch;B&&S.deps++;let T=C.vnode.el;C.asyncDep.catch(F=>{ji(F,C,0)}).then(F=>{if(C.isUnmounted||S.isUnmounted||S.pendingId!==C.suspenseId)return;zs(),C.asyncResolved=!0;let{vnode:L}=C;ua(C,F,!1),T&&(L.el=T);let M=!T&&C.subTree.el;E(C,L,u(T||C.subTree.el),T?null:b(C.subTree),S,a,O),M&&(L.placeholder=null,h(M)),yr(C,L.el),B&&--S.deps==0&&S.resolve()})},unmount(C,E){S.isUnmounted=!0,S.activeBranch&&q(S.activeBranch,i,C,E),S.pendingBranch&&q(S.pendingBranch,i,C,E)}};return S}function Rl(e){let t;if(se(e)){let i=Ai&&e._c;i&&(e._d=!1,Ls()),e=e(),i&&(e._d=!0,t=Xe,xr())}return G(e)&&(e=function(i){let s;for(let n=0;n<i.length;n++){let r=i[n];if(!Zt(r))return;if(r.type!==Re||r.children==="v-if"){if(s)return;s=r}}return s}(e)),e=ct(e),t&&!e.dynamicChildren&&(e.dynamicChildren=t.filter(i=>i!==e)),e}function Ac(e,t){t&&t.pendingBranch?G(e)?t.effects.push(...e):t.effects.push(e):Rs(e)}function Vi(e,t){e.activeBranch=t;let{vnode:i,parentComponent:s}=e,n=t.el;for(;!n&&t.component;)n=(t=t.component.subTree).el;i.el=n,s&&s.subTree===i&&(s.vnode.el=n,yr(s,n))}var $e=Symbol.for("v-fgt"),oi=Symbol.for("v-txt"),Re=Symbol.for("v-cmt"),Ti=Symbol.for("v-stc"),Qt=[],Xe=null;function Ls(e=!1){Qt.push(Xe=e?null:[])}function xr(){Qt.pop(),Xe=Qt[Qt.length-1]||null}var Ai=1;function Fs(e,t=!1){Ai+=e,e<0&&Xe&&t&&(Xe.hasOnce=!0)}function Ic(e){return e.dynamicChildren=Ai>0?Xe||Qi:null,xr(),Ai>0&&Xe&&Xe.push(e),e}function nh(e,t,i,s,n,r){return Ic(Wa(e,t,i,s,n,r,!0))}function Un(e,t,i,s,n){return Ic(Te(e,t,i,s,n,!0))}function Zt(e){return!!e&&e.__v_isVNode===!0}function Tt(e,t){return e.type===t.type&&e.key===t.key}function rh(e){}var Nc=({key:e})=>e??null,Sn=({ref:e,ref_key:t,ref_for:i})=>(typeof e=="number"&&(e=""+e),e!=null?re(e)||Le(e)||se(e)?{i:Qe,r:e,k:t,f:!!i}:e:null);function Wa(e,t=null,i=null,s=0,n=null,r=+(e!==$e),a=!1,l=!1){let o={__v_isVNode:!0,__v_skip:!0,type:e,props:t,key:t&&Nc(t),ref:t&&Sn(t),scopeId:fr,slotScopeIds:null,children:i,component:null,suspense:null,ssContent:null,ssFallback:null,dirs:null,transition:null,el:null,anchor:null,target:null,targetStart:null,targetAnchor:null,staticCount:0,shapeFlag:r,patchFlag:s,dynamicProps:n,dynamicChildren:null,appContext:null,ctx:Qe};return l?(Vn(o,i),128&r&&e.normalize(o)):i&&(o.shapeFlag|=re(i)?8:16),Ai>0&&!a&&Xe&&(o.patchFlag>0||6&r)&&o.patchFlag!==32&&Xe.push(o),o}var Te=function(e,t=null,i=null,s=0,n=null,r=!1){var a;if(e&&e!==vc||(e=Re),Zt(e)){let o=jt(e,t,!0);return i&&Vn(o,i),Ai>0&&!r&&Xe&&(6&o.shapeFlag?Xe[Xe.indexOf(e)]=o:Xe.push(o)),o.patchFlag=-2,o}if(se(a=e)&&"__vccOpts"in a&&(e=e.__vccOpts),t){let{class:o,style:c}=t=Ec(t);o&&!re(o)&&(t.class=Hs(o)),me(c)&&(Ks(c)&&!G(c)&&(c=de({},c)),t.style=Vs(c))}let l=re(e)?1:$n(e)?128:e.__isTeleport?64:me(e)?4:2*!!se(e);return Wa(e,t,i,s,n,l,r,!0)};function Ec(e){return e?Ks(e)||wc(e)?de({},e):e:null}function jt(e,t,i=!1,s=!1){let{props:n,ref:r,patchFlag:a,children:l,transition:o}=e,c=t?Rc(n||{},t):n,d={__v_isVNode:!0,__v_skip:!0,type:e.type,props:c,key:c&&Nc(c),ref:t&&t.ref?i&&r?G(r)?r.concat(Sn(t)):[r,Sn(t)]:Sn(t):r,scopeId:e.scopeId,slotScopeIds:e.slotScopeIds,children:l,target:e.target,targetStart:e.targetStart,targetAnchor:e.targetAnchor,staticCount:e.staticCount,shapeFlag:e.shapeFlag,patchFlag:t&&e.type!==$e?a===-1?16:16|a:a,dynamicProps:e.dynamicProps,dynamicChildren:e.dynamicChildren,appContext:e.appContext,dirs:e.dirs,transition:o,component:e.component,suspense:e.suspense,ssContent:e.ssContent&&jt(e.ssContent),ssFallback:e.ssFallback&&jt(e.ssFallback),placeholder:e.placeholder,el:e.el,anchor:e.anchor,ctx:e.ctx,ce:e.ce};return o&&s&&Xt(d,o.clone(d)),d}function Ja(e=" ",t=0){return Te(oi,null,e,t)}function ah(e,t){let i=Te(Ti,null,e);return i.staticCount=t,i}function Oc(e="",t=!1){return t?(Ls(),Un(Re,null,e)):Te(Re,null,e)}function ct(e){return e==null||typeof e=="boolean"?Te(Re):G(e)?Te($e,null,e.slice()):Zt(e)?Bt(e):Te(oi,null,String(e))}function Bt(e){return e.el===null&&e.patchFlag!==-1||e.memo?e:jt(e)}function Vn(e,t){let i=0,{shapeFlag:s}=e;if(t==null)t=null;else if(G(t))i=16;else if(typeof t=="object")if(65&s){let n=t.default;n&&(n._c&&(n._d=!1),Vn(e,n()),n._c&&(n._d=!0));return}else{i=32;let n=t._;n||wc(t)?n===3&&Qe&&(Qe.slots._===1?t._=1:(t._=2,e.patchFlag|=1024)):t._ctx=Qe}else if(se(t)){if(65&s)return void Vn(e,{default:t});t={default:t,_ctx:Qe},i=32}else t=String(t),64&s?(i=16,t=[Ja(t)]):i=8;e.children=t,e.shapeFlag|=i}function Rc(...e){let t={};for(let i=0;i<e.length;i++){let s=e[i];for(let n in s)if(n==="class")t.class!==s.class&&(t.class=Hs([t.class,s.class]));else if(n==="style")t.style=Vs([t.style,s.style]);else if(Ri(n)){let r=t[n],a=s[n];a&&r!==a&&!(G(r)&&r.includes(a))?t[n]=r?[].concat(r,a):a:a!=null||r!=null||nr(n)||(t[n]=a)}else n!==""&&(t[n]=s[n])}return t}function ot(e,t,i,s=null){vt(e,t,7,[i,s])}var lh=bc(),oh=0;function Pc(e,t,i){let s=e.type,n=(t?t.appContext:e.appContext)||lh,r={uid:oh++,vnode:e,type:s,parent:t,appContext:n,root:null,next:null,subTree:null,effect:null,update:null,job:null,scope:new Ns(!0),render:null,proxy:null,exposed:null,exposeProxy:null,withProxy:null,provides:t?t.provides:Object.create(n.provides),ids:t?t.ids:["",0,0],accessCache:null,renderCache:[],components:null,directives:null,propsOptions:function a(l,o,c=!1){let d=c?th:o.propsCache,p=d.get(l);if(p)return p;let f=l.props,y={},m=[],x=!1;if(!se(l)){let b=u=>{x=!0;let[h,g]=a(u,o,!0);de(y,h),g&&m.push(...g)};!c&&o.mixins.length&&o.mixins.forEach(b),l.extends&&b(l.extends),l.mixins&&l.mixins.forEach(b)}if(!f&&!x)return me(l)&&d.set(l,Qi),Qi;if(G(f))for(let b=0;b<f.length;b++){let u=ye(f[b]);El(u)&&(y[u]=pe)}else if(f)for(let b in f){let u=ye(b);if(El(u)){let h=f[b],g=y[u]=G(h)||se(h)?{type:h}:de({},h),_=g.type,k=!1,S=!0;if(G(_))for(let C=0;C<_.length;++C){let E=_[C],O=se(E)&&E.name;if(O==="Boolean"){k=!0;break}O==="String"&&(S=!1)}else k=se(_)&&_.name==="Boolean";g[0]=k,g[1]=S,(k||fe(g,"default"))&&m.push(u)}}let q=[y,m];return me(l)&&d.set(l,q),q}(s,n),emitsOptions:function a(l,o,c=!1){let d=c?Xu:o.emitsCache,p=d.get(l);if(p!==void 0)return p;let f=l.emits,y={},m=!1;if(!se(l)){let x=q=>{let b=a(q,o,!0);b&&(m=!0,de(y,b))};!c&&o.mixins.length&&o.mixins.forEach(x),l.extends&&x(l.extends),l.mixins&&l.mixins.forEach(x)}return f||m?(G(f)?f.forEach(x=>y[x]=null):de(y,f),me(l)&&d.set(l,y),y):(me(l)&&d.set(l,null),null)}(s,n),emit:null,emitted:null,propsDefaults:pe,inheritAttrs:s.inheritAttrs,ctx:pe,data:pe,props:pe,attrs:pe,slots:pe,refs:pe,setupState:pe,setupContext:null,suspense:i,suspenseId:i?i.pendingId:0,asyncDep:null,asyncResolved:!1,isMounted:!1,isUnmounted:!1,isDeactivated:!1,bc:null,c:null,bm:null,m:null,bu:null,u:null,um:null,bum:null,da:null,a:null,rtg:null,rtc:null,ec:null,sp:null};return r.ctx={_:r},r.root=t?t.root:r,r.emit=Yu.bind(null,r),e.ce&&e.ce(r),r}var Ke=null,rt=()=>Ke||Qe;{let e=or(),t=(i,s)=>{let n;return(n=e[i])||(n=e[i]=[]),n.push(s),r=>{n.length>1?n.forEach(a=>a(r)):n[0](r)}};Tn=t("__VUE_INSTANCE_SETTERS__",i=>Ke=i),Ki=t("__VUE_SSR_SETTERS__",i=>Ii=i)}var os=e=>{let t=Ke;return Tn(e),e.scope.on(),()=>{e.scope.off(),Tn(t)}},zs=()=>{Ke&&Ke.scope.off(),Tn(null)};function jc(e){return 4&e.vnode.shapeFlag}var Ii=!1;function Lc(e,t=!1,i=!1){t&&Ki(t);let{props:s,children:n}=e.vnode,r=jc(e);(function(c,d,p,f=!1){let y={},m=Object.create(ca);for(let x in c.propsDefaults=Object.create(null),kc(c,d,y,m),c.propsOptions[0])x in y||(y[x]=void 0);p?c.props=f?y:Vo(y):c.type.props?c.props=y:c.props=m,c.attrs=m})(e,s,r,t);var a=i||t;let l=e.slots=Object.create(ca);if(32&e.vnode.shapeFlag){let c=n._;c?(qc(l,n,a),a&&Mo(l,"_",c,!0)):_c(n,l)}else n&&Sc(e,n);let o=r?function(c,d){let p=c.type;c.accessCache=Object.create(null),c.proxy=new Proxy(c.ctx,ra);let{setup:f}=p;if(f){Gt();let y=c.setupContext=f.length>1?Bc(c):null,m=os(c),x=ls(f,c,0,[c.props,y]),q=Ia(x);if(Yt(),m(),(q||c.sp)&&!Kt(c)&&za(c),q){if(x.then(zs,zs),d)return x.then(b=>{ua(c,b,d)}).catch(b=>{ji(b,c,0)});c.asyncDep=x}else ua(c,x,d)}else zc(c,d)}(e,t):void 0;return t&&Ki(!1),o}function ua(e,t,i){se(t)?e.type.__ssrInlineRender?e.ssrRender=t:e.render=t:me(t)&&(e.setupState=Oa(t)),zc(e,i)}function Fc(e){Cn=e,Wr=t=>{t.render._rc&&(t.withProxy=new Proxy(t.ctx,Ru))}}var ch=()=>!Cn;function zc(e,t,i){let s=e.type;if(!e.render){if(!t&&Cn&&!s.render){let n=s.template||la(e).template;if(n){let{isCustomElement:r,compilerOptions:a}=e.appContext.config,{delimiters:l,compilerOptions:o}=s,c=de(de({isCustomElement:r,delimiters:l},a),o);s.render=Cn(n,c)}}e.render=s.render||He,Wr&&Wr(e)}{let n=os(e);Gt();try{(function(r){let a=la(r),l=r.proxy,o=r.ctx;aa=!1,a.beforeCreate&&Ml(a.beforeCreate,r,"bc");let{data:c,computed:d,methods:p,watch:f,provide:y,inject:m,created:x,beforeMount:q,mounted:b,beforeUpdate:u,updated:h,activated:g,deactivated:_,beforeUnmount:k,unmounted:S,render:C,renderTracked:E,renderTriggered:O,errorCaptured:B,serverPrefetch:T,expose:F,inheritAttrs:L,components:M,directives:Q}=a;if(m&&function(J,K){for(let te in G(J)&&(J=oa(J)),J){let ne,he=J[te];Le(ne=me(he)?"default"in he?Cs(he.from||te,he.default,!0):Cs(he.from||te):Cs(he))?Object.defineProperty(K,te,{enumerable:!0,configurable:!0,get:()=>ne.value,set:Ae=>ne.value=Ae}):K[te]=ne}}(m,o),p)for(let J in p){let K=p[J];se(K)&&(o[J]=K.bind(l))}if(c){let J=c.call(l,l);me(J)&&(r.data=ui(J))}if(aa=!0,d)for(let J in d){let K=d[J],te=se(K)?K.bind(l,l):se(K.get)?K.get.bind(l,l):He,ne=Dc({get:te,set:!se(K)&&se(K.set)?K.set.bind(l):He});Object.defineProperty(o,J,{enumerable:!0,configurable:!0,get:()=>ne.value,set:he=>ne.value=he})}if(f)for(let J in f)(function K(te,ne,he,Ae){let _e=Ae.includes(".")?ic(he,Ae):()=>he[Ae];if(re(te)){let Ve=ne[te];se(Ve)&&Zi(_e,Ve)}else if(se(te))Zi(_e,te.bind(he));else if(me(te))if(G(te))te.forEach(Ve=>K(Ve,ne,he,Ae));else{let Ve=se(te.handler)?te.handler.bind(he):ne[te.handler];se(Ve)&&Zi(_e,Ve,te)}})(f[J],o,l,J);if(y){let J=se(y)?y.call(l):y;Reflect.ownKeys(J).forEach(K=>{Xo(K,J[K])})}function V(J,K){G(K)?K.forEach(te=>J(te.bind(l))):K&&J(K.bind(l))}if(x&&Ml(x,r,"c"),V(pc,q),V(Gs,b),V(Ba,u),V(gr,h),V(oc,g),V(cc,_),V(fc,B),V(mc,E),V(hc,O),V(br,k),V(Ys,S),V(uc,T),G(F))if(F.length){let J=r.exposed||(r.exposed={});F.forEach(K=>{Object.defineProperty(J,K,{get:()=>l[K],set:te=>l[K]=te,enumerable:!0})})}else r.exposed||(r.exposed={});C&&r.render===He&&(r.render=C),L!=null&&(r.inheritAttrs=L),M&&(r.components=M),Q&&(r.directives=Q),T&&za(r)})(e)}finally{Yt(),n()}}}var dh={get:(e,t)=>(Ye(e,"get",""),e[t])};function Bc(e){return{attrs:new Proxy(e.attrs,dh),slots:e.slots,emit:e.emit,expose:t=>{e.exposed=t||{}}}}function Xs(e){return e.exposed?e.exposeProxy||(e.exposeProxy=new Proxy(Oa(Ho(e.exposed)),{get:(t,i)=>i in t?t[i]:i in Ms?Ms[i](e):void 0,has:(t,i)=>i in t||i in Ms})):e.proxy}function ha(e,t=!0){return se(e)?e.displayName||e.name:e.name||t&&e.__name}var Dc=(e,t)=>function(i,s=!1){let n,r;return se(i)?n=i:(n=i.get,r=i.set),new ia(n,r,s)}(e,Ii);function $c(e,t,i){try{Fs(-1);let s=arguments.length;return s!==2?(s>3?i=Array.prototype.slice.call(arguments,2):s===3&&Zt(i)&&(i=[i]),Te(e,t,i)):!me(t)||G(t)?Te(e,null,t):Zt(t)?Te(e,null,[t]):Te(e,t)}finally{Fs(1)}}function ph(){}function uh(e,t,i,s){let n=i[s];if(n&&Uc(n,e))return n;let r=t();return r.memo=e.slice(),r.cacheIndex=s,i[s]=r}function Uc(e,t){let i=e.memo;if(i.length!=t.length)return!1;for(let s=0;s<i.length;s++)if(De(i[s],t[s]))return!1;return Ai>0&&Xe&&Xe.push(e),!0}var Vc="3.5.40",hh=He,mh=null,fh,vh=He,gh={createComponentInstance:Pc,setupComponent:Lc,renderComponentRoot:_n,setCurrentRenderingInstance:Ps,isVNode:Zt,normalizeVNode:ct,getComponentPublicInstance:Xs,ensureValidVNode:Ua,pushWarningContext:function(e){},popWarningContext:function(){}},bh=null,yh=null,xh=null,Pl="u">typeof window&&window.trustedTypes;if(Pl)try{Jr=Pl.createPolicy("vue",{createHTML:e=>e})}catch{}var Hc=Jr?e=>Jr.createHTML(e):e=>e,zt="u">typeof document?document:null,jl=zt&&zt.createElement("template"),Kc={insert:(e,t,i)=>{t.insertBefore(e,i||null)},remove:e=>{let t=e.parentNode;t&&t.removeChild(e)},createElement:(e,t,i,s)=>{let n=t==="svg"?zt.createElementNS("http://www.w3.org/2000/svg",e):t==="mathml"?zt.createElementNS("http://www.w3.org/1998/Math/MathML",e):i?zt.createElement(e,{is:i}):zt.createElement(e);return e==="select"&&s&&s.multiple!=null&&n.setAttribute("multiple",s.multiple),n},createText:e=>zt.createTextNode(e),createComment:e=>zt.createComment(e),setText:(e,t)=>{e.nodeValue=t},setElementText:(e,t)=>{e.textContent=t},parentNode:e=>e.parentNode,nextSibling:e=>e.nextSibling,querySelector:e=>zt.querySelector(e),setScopeId(e,t){e.setAttribute(t,"")},insertStaticContent(e,t,i,s,n,r){let a=i?i.previousSibling:t.lastChild;if(n&&(n===r||n.nextSibling))for(;t.insertBefore(n.cloneNode(!0),i),n!==r&&(n=n.nextSibling););else{jl.innerHTML=Hc(s==="svg"?`<svg>${e}</svg>`:s==="mathml"?`<math>${e}</math>`:e);let l=jl.content;if(s==="svg"||s==="mathml"){let o=l.firstChild;for(;o.firstChild;)l.appendChild(o.firstChild);l.removeChild(o)}t.insertBefore(l,i)}return[a?a.nextSibling:t.firstChild,i?i.previousSibling:t.lastChild]}},ii="transition",bs="animation",ss=Symbol("_vtc"),Qc={name:String,type:String,css:{type:Boolean,default:!0},duration:[String,Number,Object],enterFromClass:String,enterActiveClass:String,enterToClass:String,appearFromClass:String,appearActiveClass:String,appearToClass:String,leaveFromClass:String,leaveActiveClass:String,leaveToClass:String},Wc=de({},La,Qc),wh=((Vr=(e,{slots:t})=>$c(ac,Jc(e),t)).displayName="Transition",Vr.props=Wc,Vr),bi=(e,t=[])=>{G(e)?e.forEach(i=>i(...t)):e&&e(...t)},Ll=e=>!!e&&(G(e)?e.some(t=>t.length>1):e.length>1);function Jc(e){let t={};for(let T in e)T in Qc||(t[T]=e[T]);if(e.css===!1)return t;let{name:i="v",type:s,duration:n,enterFromClass:r=`${i}-enter-from`,enterActiveClass:a=`${i}-enter-active`,enterToClass:l=`${i}-enter-to`,appearFromClass:o=r,appearActiveClass:c=a,appearToClass:d=l,leaveFromClass:p=`${i}-leave-from`,leaveActiveClass:f=`${i}-leave-active`,leaveToClass:y=`${i}-leave-to`}=e,m=function(T){if(T==null)return null;{if(me(T))return[function(L){return Gi(L)}(T.enter),function(L){return Gi(L)}(T.leave)];let F=function(L){return Gi(L)}(T);return[F,F]}}(n),x=m&&m[0],q=m&&m[1],{onBeforeEnter:b,onEnter:u,onEnterCancelled:h,onLeave:g,onLeaveCancelled:_,onBeforeAppear:k=b,onAppear:S=u,onAppearCancelled:C=h}=t,E=(T,F,L,M)=>{T._enterCancelled=M,ri(T,F?d:l),ri(T,F?c:a),L&&L()},O=(T,F)=>{T._isLeaving=!1,ri(T,p),ri(T,y),ri(T,f),F&&F()},B=T=>(F,L)=>{let M=T?S:u,Q=()=>E(F,T,L);bi(M,[F,Q]),Fl(()=>{ri(F,T?o:r),Nt(F,T?d:l),Ll(M)||zl(F,s,x,Q)})};return de(t,{onBeforeEnter(T){bi(b,[T]),Nt(T,r),Nt(T,a)},onBeforeAppear(T){bi(k,[T]),Nt(T,o),Nt(T,c)},onEnter:B(!1),onAppear:B(!0),onLeave(T,F){T._isLeaving=!0;let L=()=>O(T,F);Nt(T,p),T._enterCancelled?(Nt(T,f),ma(T)):(ma(T),Nt(T,f)),Fl(()=>{T._isLeaving&&(ri(T,p),Nt(T,y),Ll(g)||zl(T,s,q,L))}),bi(g,[T,L])},onEnterCancelled(T){E(T,!1,void 0,!0),bi(h,[T])},onAppearCancelled(T){E(T,!0,void 0,!0),bi(C,[T])},onLeaveCancelled(T){O(T),bi(_,[T])}})}function Nt(e,t){t.split(/\s+/).forEach(i=>i&&e.classList.add(i)),(e[ss]||(e[ss]=new Set)).add(t)}function ri(e,t){t.split(/\s+/).forEach(s=>s&&e.classList.remove(s));let i=e[ss];i&&(i.delete(t),i.size||(e[ss]=void 0))}function Fl(e){requestAnimationFrame(()=>{requestAnimationFrame(e)})}var kh=0;function zl(e,t,i,s){let n=e._endId=++kh,r=()=>{n===e._endId&&s()};if(i!=null)return setTimeout(r,i);let{type:a,timeout:l,propCount:o}=Gc(e,t);if(!a)return s();let c=a+"end",d=0,p=()=>{e.removeEventListener(c,f),r()},f=y=>{y.target===e&&++d>=o&&p()};setTimeout(()=>{d<o&&p()},l+1),e.addEventListener(c,f)}function Gc(e,t){let i=window.getComputedStyle(e),s=m=>(i[m]||"").split(", "),n=s(`${ii}Delay`),r=s(`${ii}Duration`),a=Bl(n,r),l=s(`${bs}Delay`),o=s(`${bs}Duration`),c=Bl(l,o),d=null,p=0,f=0;t===ii?a>0&&(d=ii,p=a,f=r.length):t===bs?c>0&&(d=bs,p=c,f=o.length):f=(d=(p=Math.max(a,c))>0?a>c?ii:bs:null)?d===ii?r.length:o.length:0;let y=d===ii&&/\b(?:transform|all)(?:,|$)/.test(s(`${ii}Property`).toString());return{type:d,timeout:p,propCount:f,hasTransform:y}}function Bl(e,t){for(;e.length<t.length;)e=e.concat(e);return Math.max(...t.map((i,s)=>Dl(i)+Dl(e[s])))}function Dl(e){return e==="auto"?0:1e3*Number(e.slice(0,-1).replace(",","."))}function ma(e){return(e?e.ownerDocument:document).body.offsetHeight}var Hn=Symbol("_vod"),Ga=Symbol("_vsh"),Yc={name:"show",beforeMount(e,{value:t},{transition:i}){e[Hn]=e.style.display==="none"?"":e.style.display,i&&t?i.beforeEnter(e):ys(e,t)},mounted(e,{value:t},{transition:i}){i&&t&&i.enter(e)},updated(e,{value:t,oldValue:i},{transition:s}){!t!=!i&&(s?t?(s.beforeEnter(e),ys(e,!0),s.enter(e)):s.leave(e,()=>{ys(e,!1)}):ys(e,t))},beforeUnmount(e,{value:t}){ys(e,t)}};function ys(e,t){e.style.display=t?e[Hn]:"none",e[Ga]=!t}var Xc=Symbol("");function _h(e){let t=rt();if(!t)return;let i=t.ut=(n=e(t.proxy))=>{Array.from(document.querySelectorAll(`[data-v-owner="${t.uid}"]`)).forEach(r=>fn(r,n))},s=()=>{let n=e(t.proxy);t.ce?fn(t.ce,n):function r(a,l){if(128&a.shapeFlag){let o=a.suspense;a=o.activeBranch,o.pendingBranch&&!o.isHydrating&&o.effects.push(()=>{r(o.activeBranch,l)})}for(;a.component;)a=a.component.subTree;if(1&a.shapeFlag&&a.el)fn(a.el,l);else if(a.type===$e)a.children.forEach(o=>r(o,l));else if(a.type===Ti){let{el:o,anchor:c}=a;for(;o&&(fn(o,l),o!==c);)o=o.nextSibling}}(t.subTree,n),i(n)};Ba(()=>{Rs(s)}),Gs(()=>{Zi(s,He,{flush:"post"});let n=new MutationObserver(s);n.observe(t.subTree.el.parentNode,{childList:!0}),Ys(()=>n.disconnect())})}function fn(e,t){if(e.nodeType===1){let s=e.style,n="";for(let r in t){var i;let a=(i=t[r])==null?"initial":typeof i=="string"?i===""?" ":i:String(i);s.setProperty(`--${r}`,a),n+=`--${r}: ${a};`}s[Xc]=n}}var Sh=/(?:^|;)\s*display\s*:/,$l=/\s*!important$/;function ws(e,t,i){if(G(i))i.forEach(s=>ws(e,t,s));else if(i==null&&(i=""),t.startsWith("--"))e.setProperty(t,i);else{let s=function(n,r){let a=$r[r];if(a)return a;let l=ye(r);if(l!=="filter"&&l in n)return $r[r]=l;l=Pi(l);for(let o=0;o<Ul.length;o++){let c=Ul[o]+l;if(c in n)return $r[r]=c}return r}(e,t);$l.test(i)?e.setProperty(dt(s),i.replace($l,""),"important"):e[s]=i}}var Ul=["Webkit","Moz","ms"],$r={},Vl="http://www.w3.org/1999/xlink";function Hl(e,t,i,s,n,r=Ep(t)){s&&t.startsWith("xlink:")?i==null?e.removeAttributeNS(Vl,t.slice(6,t.length)):e.setAttributeNS(Vl,t,i):i==null||r&&!(i||i==="")?e.removeAttribute(t):e.setAttribute(t,r?"":Ze(i)?String(i):i)}function Kl(e,t,i,s,n){if(t==="innerHTML"||t==="textContent"){i!=null&&(e[t]=t==="innerHTML"?Hc(i):i);return}let r=e.tagName;if(t==="value"&&r!=="PROGRESS"&&!r.includes("-")){let o=r==="OPTION"?e.getAttribute("value")||"":e.value,c=i==null?e.type==="checkbox"?"on":"":String(i);o===c&&"_value"in e||(e.value=c),i==null&&e.removeAttribute(t),e._value=i;return}let a=!1;if(i===""||i==null){let o=typeof e[t];if(o==="boolean"){var l;i=!!(l=i)||l===""}else i==null&&o==="string"?(i="",a=!0):o==="number"&&(i=0,a=!0)}try{e[t]=i}catch{}a&&e.removeAttribute(n||t)}function Ut(e,t,i,s){e.addEventListener(t,i,s)}var Ql=Symbol("_vei"),qh=/(Once|Passive|Capture)$/,Th=/^on:?(?:Once|Passive|Capture)$/,Ur=0,Ch=Promise.resolve(),Wl=e=>e.charCodeAt(0)===111&&e.charCodeAt(1)===110&&e.charCodeAt(2)>96&&123>e.charCodeAt(2),Zc=(e,t,i,s,n,r)=>{let a=n==="svg";if(t==="class"){var l;let o;l=s,(o=e[ss])&&(l=(l?[l,...o]:[...o]).join(" ")),l==null?e.removeAttribute("class"):a?e.setAttribute("class",l):e.className=l}else t==="style"?function(o,c,d){let p=o.style,f=re(d),y=!1;if(d&&!f){if(c)if(re(c))for(let u of c.split(";")){let h=u.slice(0,u.indexOf(":")).trim();d[h]==null&&ws(p,h,"")}else for(let u in c)d[u]==null&&ws(p,u,"");for(let u in d){var m,x,q,b;u==="display"&&(y=!0);let h=d[u];h!=null?(m=o,x=u,q=!re(c)&&c?c[u]:void 0,b=h,m.tagName==="TEXTAREA"&&(x==="width"||x==="height")&&re(b)&&q===b||ws(p,u,h)):ws(p,u,"")}}else if(f){if(c!==d){let u=p[Xc];u&&(d+=";"+u),p.cssText=d,y=Sh.test(d)}}else c&&o.removeAttribute("style");Hn in o&&(o[Hn]=y?p.display:"",o[Ga]&&(p.display="none"))}(e,i,s):Ri(t)?nr(t)||function(o,c,d,p=null){let f=o[Ql]||(o[Ql]={}),y=f[c];if(d&&y)y.value=d;else{let[q,b]=function(u){let h,g;for(;(g=u.match(qh))&&!Th.test(u);)h||(h={}),u=u.slice(0,u.length-g[1].length),h[g[1].toLowerCase()]=!0;return[u[2]===":"?u.slice(3):dt(u.slice(2)),h]}(c);if(d){var m,x;let u;Ut(o,q,f[c]=(m=d,x=p,(u=h=>{if(h._vts){if(h._vts<=u.attached)return}else h._vts=Date.now();let g=u.value;if(G(g)){let _=h.stopImmediatePropagation;h.stopImmediatePropagation=()=>{_.call(h),h._stopped=!0};let k=g.slice(),S=[h];for(let C=0;C<k.length&&!h._stopped;C++){let E=k[C];E&&vt(E,x,5,S)}}else vt(g,x,5,[h])}).value=m,u.attached=Ur||(Ch.then(()=>Ur=0),Ur=Date.now()),u),b)}else y&&(o.removeEventListener(q,y,b),f[c]=void 0)}}(e,t,s,r):(t[0]==="."?(t=t.slice(1),0):t[0]==="^"?(t=t.slice(1),1):!function(o,c,d,p){if(p)return!!(c==="innerHTML"||c==="textContent"||c in o&&Wl(c)&&se(d));if(c==="spellcheck"||c==="draggable"||c==="translate"||c==="autocorrect"||c==="sandbox"&&o.tagName==="IFRAME"||c==="form"||c==="list"&&o.tagName==="INPUT"||c==="type"&&o.tagName==="TEXTAREA")return!1;if(c==="width"||c==="height"){let f=o.tagName;if(f==="IMG"||f==="VIDEO"||f==="CANVAS"||f==="SOURCE")return!1}return!(Wl(c)&&re(d))&&c in o}(e,t,s,a))?e._isVueCE&&(function(o,c){let d=o._def.props;if(!d)return!1;let p=ye(c);return Array.isArray(d)?d.some(f=>ye(f)===p):Object.keys(d).some(f=>ye(f)===p)}(e,t)||e._def.__asyncLoader&&(/[A-Z]/.test(t)||!re(s)))?Kl(e,ye(t),s,r,t):(t==="true-value"?e._trueValue=s:t==="false-value"&&(e._falseValue=s),Hl(e,t,s,a)):(Kl(e,t,s),e.tagName.includes("-")||t!=="value"&&t!=="checked"&&t!=="selected"||Hl(e,t,s,a,r,t!=="value"))},Jl={};function ed(e,t,i){let s,n=Fa(e,t);s=n,Me.call(s)==="[object Object]"&&(n=de({},n,t));class r extends Kn{constructor(l){super(n,l,i)}}return r.def=n,r}var Mh=(e,t)=>ed(e,t,pd),Ah="u">typeof HTMLElement?HTMLElement:class{},Kn=class e extends Ah{constructor(t,i={},s=Bs){super(),this._def=t,this._props=i,this._createApp=s,this._isVueCE=!0,this._instance=null,this._app=null,this._nonce=this._def.nonce,this._connected=!1,this._resolved=!1,this._patching=!1,this._dirty=!1,this._numberProps=null,this._styleChildren=new WeakSet,this._styleAnchors=new WeakMap,this._ob=null,this.shadowRoot&&s!==Bs?this._root=this.shadowRoot:t.shadowRoot!==!1?(this.attachShadow(de({},t.shadowRootOptions,{mode:"open"})),this._root=this.shadowRoot):this._root=this}connectedCallback(){if(!this.isConnected)return;this.shadowRoot||this._resolved||this._parseSlots(),this._connected=!0;let t=this;for(;t=t&&(t.assignedSlot||t.parentNode||t.host);)if(t instanceof e){this._parent=t;break}this._instance||(this._resolved?this._mount(this._def):t&&t._pendingResolve?this._pendingResolve=t._pendingResolve.then(()=>{this._pendingResolve=void 0,this._resolveDef()}):this._resolveDef())}_setParent(t=this._parent){t&&(this._instance.parent=t._instance,this._inheritParentContext(t))}_inheritParentContext(t=this._parent){t&&this._app&&Object.setPrototypeOf(this._app._context.provides,t._instance.provides)}disconnectedCallback(){this._connected=!1,mr(()=>{!this._connected&&(this._ob&&(this._ob.disconnect(),this._ob=null),this._app&&this._app.unmount(),this._instance&&(this._instance.ce=void 0),this._app=this._instance=null,this._teleportTargets&&(this._teleportTargets.clear(),this._teleportTargets=void 0))})}_processMutations(t){for(let i of t)this._setAttr(i.attributeName)}_resolveDef(){if(this._pendingResolve)return;for(let s=0;s<this.attributes.length;s++)this._setAttr(this.attributes[s].name);this._ob=new MutationObserver(this._processMutations.bind(this)),this._ob.observe(this,{attributes:!0});let t=(s,n=!1)=>{let r;this._resolved=!0,this._pendingResolve=void 0;let{props:a,styles:l}=s;if(a&&!G(a))for(let o in a){let c=a[o];(c===Number||c&&c.type===Number)&&(o in this._props&&(this._props[o]=Gi(this._props[o])),(r||(r=Object.create(null)))[ye(o)]=!0)}this._numberProps=r,this._resolveProps(s),this.shadowRoot&&this._applyStyles(l),this._mount(s)},i=this._def.__asyncLoader;i?this._pendingResolve=i().then(s=>{s.configureApp=this._def.configureApp,t(this._def=s,!0)}):t(this._def)}_mount(t){this._app=this._createApp(t),this._inheritParentContext(),t.configureApp&&t.configureApp(this._app),this._app._ceVNode=this._createVNode(),this._app.mount(this._root);let i=this._instance&&this._instance.exposed;if(i)for(let s in i)fe(this,s)||Object.defineProperty(this,s,{get:()=>Qs(i[s])})}_resolveProps(t){let{props:i}=t,s=G(i)?i:Object.keys(i||{});for(let n of Object.keys(this))n[0]!=="_"&&s.includes(n)&&this._setProp(n,this[n]);for(let n of s.map(ye))Object.defineProperty(this,n,{get(){return this._getProp(n)},set(r){this._setProp(n,r,!0,!this._patching)}})}_setAttr(t){if(t.startsWith("data-v-"))return;let i=this.hasAttribute(t),s=i?this.getAttribute(t):Jl,n=ye(t);i&&this._numberProps&&this._numberProps[n]&&(s=Gi(s)),this._setProp(n,s,!1,!0)}_getProp(t){return this._props[t]}_setProp(t,i,s=!0,n=!1){if(i!==this._props[t]&&(this._dirty=!0,i===Jl?delete this._props[t]:(this._props[t]=i,t==="key"&&this._app&&(this._app._ceVNode.key=i)),n&&this._instance&&this._update(),s)){let r=this._ob;r&&(this._processMutations(r.takeRecords()),r.disconnect()),i===!0?this.setAttribute(dt(t),""):typeof i=="string"||typeof i=="number"?this.setAttribute(dt(t),i+""):i||this.removeAttribute(dt(t)),r&&r.observe(this,{attributes:!0})}}_update(){let t=this._createVNode();this._app&&(t.appContext=this._app._context),dd(t,this._root)}_createVNode(){let t={};this.shadowRoot||(t.onVnodeMounted=t.onVnodeUpdated=this._renderSlots.bind(this));let i=Te(this._def,de(t,this._props));return this._instance||(i.ce=s=>{this._instance=s,s.ce=this,s.isCE=!0;let n=(r,a)=>{let l;this.dispatchEvent(new CustomEvent(r,(l=a[0],Me.call(l)==="[object Object]"?de({detail:a},a[0]):{detail:a})))};s.emit=(r,...a)=>{n(r,a),dt(r)!==r&&n(dt(r),a)},this._setParent()}),i}_applyStyles(t,i,s){if(!t)return;if(i){if(i===this._def||this._styleChildren.has(i))return;this._styleChildren.add(i)}let n=this._nonce,r=this.shadowRoot,a=s?this._getStyleAnchor(s)||this._getStyleAnchor(this._def):this._getRootStyleInsertionAnchor(r),l=null;for(let o=t.length-1;o>=0;o--){let c=document.createElement("style");n&&c.setAttribute("nonce",n),c.textContent=t[o],r.insertBefore(c,l||a),l=c,o===0&&(s||this._styleAnchors.set(this._def,c),i&&this._styleAnchors.set(i,c))}}_getStyleAnchor(t){if(!t)return null;let i=this._styleAnchors.get(t);return i&&i.parentNode===this.shadowRoot?i:(i&&this._styleAnchors.delete(t),null)}_getRootStyleInsertionAnchor(t){for(let i=0;i<t.childNodes.length;i++){let s=t.childNodes[i];if(!(s instanceof HTMLStyleElement))return s}return null}_parseSlots(){let t,i=this._slots={};for(;t=this.firstChild;){let s=t.nodeType===1&&t.getAttribute("slot")||"default";(i[s]||(i[s]=[])).push(t),this.removeChild(t)}}_renderSlots(){let t=this._getSlots(),i=this._instance.type.__scopeId;for(let s=0;s<t.length;s++){let n=t[s],r=n.getAttribute("name")||"default",a=this._slots[r],l=n.parentNode;if(a)for(let o of a){if(i&&o.nodeType===1){let c,d=i+"-s",p=document.createTreeWalker(o,1);for(o.setAttribute(d,"");c=p.nextNode();)c.setAttribute(d,"")}l.insertBefore(o,n)}else for(;n.firstChild;)l.insertBefore(n.firstChild,n);l.removeChild(n)}}_getSlots(){let t=[this];this._teleportTargets&&t.push(...this._teleportTargets);let i=new Set;for(let s of t){let n=s.querySelectorAll("slot");for(let r=0;r<n.length;r++)i.add(n[r])}return Array.from(i)}_injectChildStyle(t,i){this._applyStyles(t.styles,t,i)}_beginPatch(){this._patching=!0,this._dirty=!1}_endPatch(){this._patching=!1,this._dirty&&this._instance&&this._update()}_hasShadowRoot(){return this._def.shadowRoot!==!1}_removeChildStyle(t){}};function td(e){let t=rt();return t&&t.ce||null}function Ih(){let e=td();return e&&e.shadowRoot}function Nh(e="$style"){{let t=rt();if(!t)return pe;let i=t.type.__cssModules;return i&&i[e]||pe}}var id=new WeakMap,sd=new WeakMap,Qn=Symbol("_moveCb"),Gl=Symbol("_enterCb"),Eh=(Hr={name:"TransitionGroup",props:de({},Wc,{tag:String,moveClass:String}),setup(e,{slots:t}){let i,s,n=rt(),r=ja();return gr(()=>{if(!i.length)return;let a=e.moveClass||`${e.name||"v"}-move`;if(!function(o,c,d){let p=o.cloneNode(),f=o[ss];f&&f.forEach(x=>{x.split(/\s+/).forEach(q=>q&&p.classList.remove(q))}),d.split(/\s+/).forEach(x=>x&&p.classList.add(x)),p.style.display="none";let y=c.nodeType===1?c:c.parentNode;y.appendChild(p);let{hasTransform:m}=Gc(p);return y.removeChild(p),m}(i[0].el,n.vnode.el,a)){i=[];return}i.forEach(Oh),i.forEach(Rh);let l=i.filter(Ph);ma(n.vnode.el),l.forEach(o=>{let c=o.el,d=c.style;Nt(c,a),d.transform=d.webkitTransform=d.transitionDuration="";let p=c[Qn]=f=>{(!f||f.target===c)&&(!f||f.propertyName.endsWith("transform"))&&(c.removeEventListener("transitionend",p),c[Qn]=null,ri(c,a))};c.addEventListener("transitionend",p)}),i=[]}),()=>{let a=ue(e),l=Jc(a),o=a.tag||$e;if(i=[],s)for(let c=0;c<s.length;c++){let d=s[c];d.el&&d.el instanceof Element&&!d.el[Ga]&&(i.push(d),Xt(d,is(d,l,r,n)),id.set(d,nd(d.el)))}s=t.default?vr(t.default()):[];for(let c=0;c<s.length;c++){let d=s[c];d.key!=null&&Xt(d,is(d,l,r,n))}return Te(o,null,s)}}},delete Hr.props.mode,Hr);function Oh(e){let t=e.el;t[Qn]&&t[Qn](),t[Gl]&&t[Gl]()}function Rh(e){sd.set(e,nd(e.el))}function Ph(e){let t=id.get(e),i=sd.get(e),s=t.left-i.left,n=t.top-i.top;if(s||n){let r=e.el,a=r.style,l=r.getBoundingClientRect(),o=1,c=1;return r.offsetWidth&&(o=l.width/r.offsetWidth),r.offsetHeight&&(c=l.height/r.offsetHeight),Number.isFinite(o)&&o!==0||(o=1),Number.isFinite(c)&&c!==0||(c=1),.01>Math.abs(o-1)&&(o=1),.01>Math.abs(c-1)&&(c=1),a.transform=a.webkitTransform=`translate(${s/o}px,${n/c}px)`,a.transitionDuration="0s",e}}function nd(e){let t=e.getBoundingClientRect();return{left:t.left,top:t.top}}var ci=e=>{let t=e.props["onUpdate:modelValue"]||!1;return G(t)?i=>Ji(t,i):t};function jh(e){e.target.composing=!0}function Yl(e){let t=e.target;t.composing&&(t.composing=!1,t.dispatchEvent(new Event("input")))}var qt=Symbol("_assign");function Xl(e,t,i){return t&&(e=e.trim()),i&&(e=lr(e)),e}var Wn={created(e,{modifiers:{lazy:t,trim:i,number:s}},n){e[qt]=ci(n);let r=s||n.props&&n.props.type==="number";Ut(e,t?"change":"input",a=>{a.target.composing||e[qt](Xl(e.value,i,r))}),(i||r)&&Ut(e,"change",()=>{e.value=Xl(e.value,i,r)}),t||(Ut(e,"compositionstart",jh),Ut(e,"compositionend",Yl),Ut(e,"change",Yl))},mounted(e,{value:t}){e.value=t??""},beforeUpdate(e,{value:t,oldValue:i,modifiers:{lazy:s,trim:n,number:r}},a){if(e[qt]=ci(a),e.composing)return;let l=(r||e.type==="number")&&!/^0\d/.test(e.value)?lr(e.value):e.value,o=t??"";if(l===o)return;let c=e.getRootNode();(c instanceof Document||c instanceof ShadowRoot)&&c.activeElement===e&&e.type!=="range"&&(s&&t===i||n&&e.value.trim()===o)||(e.value=o)}},Ya={deep:!0,created(e,t,i){e[qt]=ci(i),Ut(e,"change",()=>{let s=e._modelValue,n=ns(e),r=e.checked,a=e[qt];if(G(s)){let l=cr(s,n),o=l!==-1;if(r&&!o)a(s.concat(n));else if(!r&&o){let c=[...s];c.splice(l,1),a(c)}}else{let l;if(l=s,Me.call(l)==="[object Set]"){let o=new Set(s);r?o.add(n):o.delete(n),a(o)}else a(ad(e,r))}})},mounted:Zl,beforeUpdate(e,t,i){e[qt]=ci(i),Zl(e,t,i)}};function Zl(e,{value:t,oldValue:i},s){let n;if(e._modelValue=t,G(t))n=cr(t,s.props.value)>-1;else{let r;if(r=t,Me.call(r)==="[object Set]")n=t.has(s.props.value);else{if(t===i)return;n=Jt(t,ad(e,!0))}}e.checked!==n&&(e.checked=n)}var Xa={created(e,{value:t},i){e.checked=Jt(t,i.props.value),e[qt]=ci(i),Ut(e,"change",()=>{e[qt](ns(e))})},beforeUpdate(e,{value:t,oldValue:i},s){e[qt]=ci(s),t!==i&&(e.checked=Jt(t,s.props.value))}},rd={deep:!0,created(e,{value:t,modifiers:{number:i}},s){e._modelValue=t,Ut(e,"change",()=>{let n,r=Array.prototype.filter.call(e.options,a=>a.selected).map(a=>i?lr(ns(a)):ns(a));e[qt](e.multiple?(n=e._modelValue,Me.call(n)==="[object Set]"?new Set(r):r):r[0]),e._assigning=!0,mr(()=>{e._assigning=!1})}),e[qt]=ci(s)},mounted(e,{value:t}){eo(e,t)},beforeUpdate(e,{value:t},i){e._modelValue=t,e[qt]=ci(i)},updated(e,{value:t}){e._assigning||eo(e,t)}};function eo(e,t){let i,s=e.multiple,n=G(t);if(!s||n||(i=t,Me.call(i)==="[object Set]")){for(let r=0,a=e.options.length;r<a;r++){let l=e.options[r],o=ns(l);if(s)if(n){let c=typeof o;c==="string"||c==="number"?l.selected=t.some(d=>String(d)===String(o)):l.selected=cr(t,o)>-1}else l.selected=t.has(o);else if(Jt(ns(l),t)){e.selectedIndex!==r&&(e.selectedIndex=r);return}}s||e.selectedIndex===-1||(e.selectedIndex=-1)}}function ns(e){return"_value"in e?e._value:e.value}function ad(e,t){let i=t?"_trueValue":"_falseValue";return i in e?e[i]:t}var ld={created(e,t,i){vn(e,t,i,null,"created")},mounted(e,t,i){vn(e,t,i,null,"mounted")},beforeUpdate(e,t,i,s){vn(e,t,i,s,"beforeUpdate")},updated(e,t,i,s){vn(e,t,i,s,"updated")}};function od(e,t){switch(e){case"SELECT":return rd;case"TEXTAREA":return Wn;default:switch(t){case"checkbox":return Ya;case"radio":return Xa;default:return Wn}}}function vn(e,t,i,s,n){let r=od(e.tagName,i.props&&i.props.type)[n];r&&r(e,t,i,s)}var Lh=["ctrl","shift","alt","meta"],Fh={stop:e=>e.stopPropagation(),prevent:e=>e.preventDefault(),self:e=>e.target!==e.currentTarget,ctrl:e=>!e.ctrlKey,shift:e=>!e.shiftKey,alt:e=>!e.altKey,meta:e=>!e.metaKey,left:e=>"button"in e&&e.button!==0,middle:e=>"button"in e&&e.button!==1,right:e=>"button"in e&&e.button!==2,exact:(e,t)=>Lh.some(i=>e[`${i}Key`]&&!t.includes(i))},zh=(e,t)=>{if(!e)return e;let i=e._withMods||(e._withMods={}),s=t.join(".");return i[s]||(i[s]=(n,...r)=>{for(let a=0;a<t.length;a++){let l=Fh[t[a]];if(l&&l(n,t))return}return e(n,...r)})},Bh={esc:"escape",space:" ",up:"arrow-up",left:"arrow-left",right:"arrow-right",down:"arrow-down",delete:"backspace"},Dh=(e,t)=>{let i=e._withKeys||(e._withKeys={}),s=t.join(".");return i[s]||(i[s]=n=>{if(!("key"in n))return;let r=dt(n.key);if(t.some(a=>a===r||Bh[a]===r))return e(n)})},Za=de({patchProp:Zc},Kc),to=!1;function cd(){return _i=to?_i:Tc(Za),to=!0,_i}var dd=(...e)=>{(_i||(_i=Ka(Za))).render(...e)},$h=(...e)=>{cd().hydrate(...e)},Bs=(...e)=>{let t=(_i||(_i=Ka(Za))).createApp(...e),{mount:i}=t;return t.mount=s=>{let n=hd(s);if(!n)return;let r=t._component;se(r)||r.render||r.template||(r.template=n.innerHTML),n.nodeType===1&&(n.textContent="");let a=i(n,!1,ud(n));return n instanceof Element&&(n.removeAttribute("v-cloak"),n.setAttribute("data-v-app","")),a},t},pd=(...e)=>{let t=cd().createApp(...e),{mount:i}=t;return t.mount=s=>{let n=hd(s);if(n)return i(n,!0,ud(n))},t};function ud(e){return e instanceof SVGElement?"svg":typeof MathMLElement=="function"&&e instanceof MathMLElement?"mathml":void 0}function hd(e){return re(e)?document.querySelector(e):e}var io=!1,Uh=()=>{io||(io=!0,Wn.getSSRProps=({value:e})=>({value:e}),Xa.getSSRProps=({value:e},t)=>{if(t.props&&Jt(t.props.value,e))return{checked:!0}},Ya.getSSRProps=({value:e},t)=>{if(G(e)){if(t.props&&cr(e,t.props.value)>-1)return{checked:!0}}else{let i;if(i=e,Me.call(i)==="[object Set]"){if(t.props&&e.has(t.props.value))return{checked:!0}}else if(e)return{checked:!0}}},ld.getSSRProps=(e,t)=>{if(typeof t.type!="string")return;let i=od(t.type.toUpperCase(),t.props&&t.props.type);if(i.getSSRProps)return i.getSSRProps(e,t)},Yc.getSSRProps=({value:e})=>{if(!e)return{style:{display:"none"}}})},Vr,Hr,so,Vh=Object.freeze({__proto__:null,BaseTransition:ac,BaseTransitionPropsValidators:La,Comment:Re,DeprecationTypes:xh,EffectScope:Ns,ErrorCodes:ru,ErrorTypeStrings:mh,Fragment:$e,KeepAlive:Tu,ReactiveEffect:Mi,Static:Ti,Suspense:sh,Teleport:mu,Text:oi,TrackOpTypes:tu,Transition:wh,TransitionGroup:Eh,TriggerOpTypes:iu,VueElement:Kn,assertNumber:nu,callWithAsyncErrorHandling:vt,callWithErrorHandling:ls,camelize:ye,capitalize:Pi,cloneVNode:jt,compatUtils:yh,computed:Dc,createApp:Bs,createBlock:Un,createCommentVNode:Oc,createElementBlock:nh,createElementVNode:Wa,createHydrationRenderer:Tc,createPropsRestProxy:Ku,createRenderer:Ka,createSSRApp:pd,createSlots:Nu,createStaticVNode:ah,createTextVNode:Ja,createVNode:Te,customRef:Wo,defineAsyncComponent:qu,defineComponent:Fa,defineCustomElement:ed,defineEmits:ju,defineExpose:Lu,defineModel:Bu,defineOptions:Fu,defineProps:Pu,defineSSRCustomElement:Mh,defineSlots:zu,devtools:fh,effect:Pp,effectScope:Op,getCurrentInstance:rt,getCurrentScope:Oo,getCurrentWatcher:su,getTransitionRawChildren:vr,guardReactiveProps:Ec,h:$c,handleError:ji,hasInjectionContext:du,hydrate:$h,hydrateOnIdle:wu,hydrateOnInteraction:Su,hydrateOnMediaQuery:_u,hydrateOnVisible:ku,initCustomFormatter:ph,initDirectivesForSSR:Uh,inject:Cs,isMemoSame:Uc,isProxy:Ks,isReactive:Ht,isReadonly:Pt,isRef:Le,isRuntimeOnly:ch,isShallow:ut,isVNode:Zt,markRaw:Ho,mergeDefaults:Vu,mergeModels:Hu,mergeProps:Rc,nextTick:mr,nodeOps:Kc,normalizeClass:Hs,normalizeProps:Cp,normalizeStyle:Vs,onActivated:oc,onBeforeMount:pc,onBeforeUnmount:br,onBeforeUpdate:Ba,onDeactivated:cc,onErrorCaptured:fc,onMounted:Gs,onRenderTracked:mc,onRenderTriggered:hc,onScopeDispose:Rp,onServerPrefetch:uc,onUnmounted:Ys,onUpdated:gr,onWatcherCleanup:Jo,openBlock:Ls,patchProp:Zc,popScopeId:lu,provide:Xo,proxyRefs:Oa,pushScopeId:au,queuePostFlushCb:Rs,reactive:ui,readonly:En,ref:qs,registerRuntimeCompiler:Fc,render:dd,renderList:Iu,renderSlot:Eu,resolveComponent:Cu,resolveDirective:Au,resolveDynamicComponent:Mu,resolveFilter:bh,resolveTransitionHooks:is,setBlockTracking:Fs,setDevtoolsHook:vh,setTransitionHooks:Xt,shallowReactive:Vo,shallowReadonly:Jp,shallowRef:Ko,ssrContextKey:Zo,ssrUtils:gh,stop:jp,toDisplayString:No,toHandlerKey:Wi,toHandlers:Ou,toRaw:ue,toRef:eu,toRefs:Zp,toValue:Yp,transformVNodeArgs:rh,triggerRef:Gp,unref:Qs,useAttrs:Uu,useCssModule:Nh,useCssVars:_h,useHost:td,useId:fu,useModel:Gu,useSSRContext:ec,useShadowRoot:Ih,useSlots:$u,useTemplateRef:vu,useTransitionState:ja,vModelCheckbox:Ya,vModelDynamic:ld,vModelRadio:Xa,vModelSelect:rd,vModelText:Wn,vShow:Yc,version:Vc,warn:hh,watch:Zi,watchEffect:pu,watchPostEffect:uu,watchSyncEffect:tc,withAsyncContext:Qu,withCtx:Pa,withDefaults:Du,withDirectives:cu,withKeys:Dh,withMemo:uh,withModifiers:zh,withScopeId:ou}),Ds=Symbol(""),Is=Symbol(""),el=Symbol(""),Jn=Symbol(""),md=Symbol(""),Ni=Symbol(""),Ei=Symbol(""),Oi=Symbol(""),di=Symbol(""),pi=Symbol(""),Zs=Symbol(""),tl=Symbol(""),fd=Symbol(""),il=Symbol(""),fa=Symbol(""),sl=Symbol(""),Hh=Symbol(""),nl=Symbol(""),rl=Symbol(""),vd=Symbol(""),gd=Symbol(""),wr=Symbol(""),Gn=Symbol(""),al=Symbol(""),ll=Symbol(""),$s=Symbol(""),en=Symbol(""),ol=Symbol(""),va=Symbol(""),Kh=Symbol(""),ga=Symbol(""),Yn=Symbol(""),Qh=Symbol(""),Wh=Symbol(""),cl=Symbol(""),Jh=Symbol(""),Gh=Symbol(""),dl=Symbol(""),bd=Symbol(""),rs={[Ds]:"Fragment",[Is]:"Teleport",[el]:"Suspense",[Jn]:"KeepAlive",[md]:"BaseTransition",[Ni]:"openBlock",[Ei]:"createBlock",[Oi]:"createElementBlock",[di]:"createVNode",[pi]:"createElementVNode",[Zs]:"createCommentVNode",[tl]:"createTextVNode",[fd]:"createStaticVNode",[il]:"resolveComponent",[fa]:"resolveDynamicComponent",[sl]:"resolveDirective",[Hh]:"resolveFilter",[nl]:"withDirectives",[rl]:"renderList",[vd]:"renderSlot",[gd]:"createSlots",[wr]:"toDisplayString",[Gn]:"mergeProps",[al]:"normalizeClass",[ll]:"normalizeStyle",[$s]:"normalizeProps",[en]:"guardReactiveProps",[ol]:"toHandlers",[va]:"camelize",[Kh]:"capitalize",[ga]:"toHandlerKey",[Yn]:"setBlockTracking",[Qh]:"pushScopeId",[Wh]:"popScopeId",[cl]:"withCtx",[Jh]:"unref",[Gh]:"isRef",[dl]:"withMemo",[bd]:"isMemoSame"},gt={start:{line:1,column:1,offset:0},end:{line:1,column:1,offset:0},source:""};function Us(e,t,i,s,n,r,a,l=!1,o=!1,c=!1,d=gt){var p,f,y,m;return e&&(l?(e.helper(Ni),e.helper((p=e.inSSR,f=c,p||f?Ei:Oi))):e.helper((y=e.inSSR,m=c,y||m?di:pi)),a&&e.helper(nl)),{type:13,tag:t,props:i,children:s,patchFlag:n,dynamicProps:r,directives:a,isBlock:l,disableTracking:o,isComponent:c,loc:d}}function Ci(e,t=gt){return{type:17,loc:t,elements:e}}function St(e,t=gt){return{type:15,loc:t,properties:e}}function je(e,t){return{type:16,loc:gt,key:re(e)?oe(e,!0):e,value:t}}function oe(e,t=!1,i=gt,s=0){return{type:4,loc:i,content:e,isStatic:t,constType:t?3:s}}function At(e,t=gt){return{type:8,loc:t,children:e}}function ze(e,t=[],i=gt){return{type:14,loc:i,callee:e,arguments:t}}function as(e,t,i=!1,s=!1,n=gt){return{type:18,params:e,returns:t,newline:i,isSlot:s,loc:n}}function ba(e,t,i,s=!0){return{type:19,test:e,consequent:t,alternate:i,newline:s,loc:gt}}function pl(e,{helper:t,removeHelper:i,inSSR:s}){if(!e.isBlock){var n,r;e.isBlock=!0,i((n=e.isComponent,s||n?di:pi)),t(Ni),t((r=e.isComponent,s||r?Ei:Oi))}}var no=new Uint8Array([123,123]),ro=new Uint8Array([125,125]);function ao(e){return e>=97&&e<=122||e>=65&&e<=90}function mt(e){return e===32||e===10||e===9||e===12||e===13}function si(e){return e===47||e===62||mt(e)}function Xn(e){let t=new Uint8Array(e.length);for(let i=0;i<e.length;i++)t[i]=e.charCodeAt(i);return t}var We={Cdata:new Uint8Array([67,68,65,84,65,91]),CdataEnd:new Uint8Array([93,93,62]),CommentEnd:new Uint8Array([45,45,62]),ScriptEnd:new Uint8Array([60,47,115,99,114,105,112,116]),StyleEnd:new Uint8Array([60,47,115,116,121,108,101]),TitleEnd:new Uint8Array([60,47,116,105,116,108,101]),TextareaEnd:new Uint8Array([60,47,116,101,120,116,97,114,101,97])};function ya(e){throw e}function yd(e){}function be(e,t,i,s){let n=SyntaxError(`https://vuejs.org/error-reference/#compiler-${e}`);return n.code=e,n.loc=t,n}var pt=e=>e.type===4&&e.isStatic;function xd(e){switch(e){case"Teleport":case"teleport":return Is;case"Suspense":case"suspense":return el;case"KeepAlive":case"keep-alive":return Jn;case"BaseTransition":case"base-transition":return md}}var xa=/^$|^\d|[^\$\w\xA0-\uFFFF]/,wd=/[A-Za-z_$\xA0-\uFFFF]/,Yh=/[\.\?\w$\xA0-\uFFFF]/,Xh=/\s+[.[]\s*|\s*[.[]\s+/g,kd=e=>e.type===4?e.content:e.loc.source,_d=e=>{let t=kd(e).trim().replace(Xh,l=>l.trim()),i=0,s=[],n=0,r=0,a=null;for(let l=0;l<t.length;l++){let o=t.charAt(l);switch(i){case 0:if(o==="[")s.push(i),i=1,n++;else if(o==="(")s.push(i),i=2,r++;else if(!(l===0?wd:Yh).test(o))return!1;break;case 1:o==="'"||o==='"'||o==="`"?(s.push(i),i=3,a=o):o==="["?n++:o!=="]"||--n||(i=s.pop());break;case 2:if(o==="'"||o==='"'||o==="`")s.push(i),i=3,a=o;else if(o==="(")r++;else if(o===")"){if(l===t.length-1)return!1;--r||(i=s.pop())}break;case 3:o===a&&(i=s.pop(),a=null)}}return!n&&!r},Zh=/^\s*(?:async\s*)?(?:\([^)]*?\)|[\w$_]+)\s*(?::[^=]+)?=>|^\s*(?:async\s+)?function(?:\s+[\w$]+)?\s*\(/;function _t(e,t,i=!1){for(let s=0;s<e.props.length;s++){let n=e.props[s];if(n.type===7&&(i||n.exp)&&(re(t)?n.name===t:t.test(n.name)))return n}}function kr(e,t,i=!1,s=!1){for(let n=0;n<e.props.length;n++){let r=e.props[n];if(r.type===6){if(i)continue;if(r.name===t&&(r.value||s))return r}else if(r.name==="bind"&&(r.exp||s)&&Hi(r.arg,t))return r}}function Hi(e,t){return!!(e&&pt(e)&&e.content===t)}function Kr(e){return e.type===5||e.type===2}function lo(e){return e.type===7&&e.name==="pre"}function em(e){return e.type===7&&e.name==="slot"}function Zn(e){return e.type===1&&e.tagType===3}function er(e){return e.type===1&&e.tagType===2}var tm=new Set([$s,en]);function wa(e,t=[]){if(e&&!re(e)&&e.type===14){let i=e.callee;if(!re(i)&&tm.has(i))return wa(e.arguments[0],t.concat(e))}return[e,t]}function tr(e,t,i){let s,n;if(e.type!==13&&function(l,o){var c,d,p;if(o.key.type!==4||o.key.content!=="key")return!1;let f=l.arguments[2];if(f&&!re(f)){let[y]=wa(f);if(y&&!re(y)&&y.type===15&&Qr(o,y))return!0}return(c=l.arguments)[2]||(c[2]="{}"),(d=l.arguments)[3]||(d[3]="undefined"),(p=l.arguments)[4]||(p[4]="undefined"),l.arguments[5]=o.value,!0}(e,t))return;let r=e.type===13?e.props:e.arguments[2],a=[];if(r&&!re(r)&&r.type===14){let l=wa(r);r=l[0],n=(a=l[1])[a.length-1]}if(r==null||re(r))s=St([t]);else if(r.type===14){let l=r.arguments[0];re(l)||l.type!==15?r.callee===ol?s=ze(i.helper(Gn),[St([t]),r]):r.arguments.unshift(St([t])):Qr(t,l)||l.properties.unshift(t),s||(s=r)}else r.type===15?(Qr(t,r)||r.properties.unshift(t),s=r):(s=ze(i.helper(Gn),[St([t]),r]),n&&n.callee===en&&(n=a[a.length-2]));e.type===13?n?n.arguments[0]=s:e.props=s:n?n.arguments[0]=s:e.arguments[2]=s}function Qr(e,t){let i=!1;if(e.key.type===4){let s=e.key.content;i=t.properties.some(n=>n.key.type===4&&n.key.content===s)}return i}function ka(e,t){return`_${t}_${e.replace(/[^\w]/g,(i,s)=>i==="-"?"_":e.charCodeAt(s).toString())}`}var im=/([\s\S]*?)\s+(?:in|of)\s+(\S[\s\S]*)/;function Sd(e){for(let t=0;t<e.length;t++)if(!mt(e.charCodeAt(t)))return!1;return!0}function ul(e){return e.type===2&&Sd(e.content)||e.type===12&&ul(e.content)}function qd(e){return e.type===3||ul(e)}var Td={parseMode:"base",ns:0,delimiters:["{{","}}"],getNamespace:()=>0,isVoidTag:$i,isPreTag:$i,isIgnoreNewlineTag:$i,isCustomElement:$i,onError:ya,onWarn:yd,comments:!1,prefixIdentifiers:!1},we=Td,ir=null,Wt="",Ge=null,ve=null,ht="",Ft=-1,xi=-1,hl=0,wi=!1,_a=null,qe=[],Oe=new class{constructor(e,t){this.stack=e,this.cbs=t,this.state=1,this.buffer="",this.sectionStart=0,this.index=0,this.entityStart=0,this.baseState=1,this.inRCDATA=!1,this.inXML=!1,this.inVPre=!1,this.newlines=[],this.mode=0,this.delimiterOpen=no,this.delimiterClose=ro,this.delimiterIndex=-1,this.currentSequence=void 0,this.sequenceIndex=0}get inSFCRoot(){return this.mode===2&&this.stack.length===0}reset(){this.state=1,this.mode=0,this.buffer="",this.sectionStart=0,this.index=0,this.baseState=1,this.inRCDATA=!1,this.currentSequence=void 0,this.newlines.length=0,this.delimiterOpen=no,this.delimiterClose=ro}getPos(e){let t=1,i=e+1,s=this.newlines.length,n=-1;if(s>100){let r=-1,a=s;for(;r+1<a;){let l=r+a>>>1;this.newlines[l]<e?r=l:a=l}n=r}else for(let r=s-1;r>=0;r--)if(e>this.newlines[r]){n=r;break}return n>=0&&(t=n+2,i=e-this.newlines[n]),{column:i,line:t,offset:e}}peek(){return this.buffer.charCodeAt(this.index+1)}stateText(e){e===60?(this.index>this.sectionStart&&this.cbs.ontext(this.sectionStart,this.index),this.state=5,this.sectionStart=this.index):this.inVPre||e!==this.delimiterOpen[0]||(this.state=2,this.delimiterIndex=0,this.stateInterpolationOpen(e))}stateInterpolationOpen(e){if(e===this.delimiterOpen[this.delimiterIndex])if(this.delimiterIndex===this.delimiterOpen.length-1){let t=this.index+1-this.delimiterOpen.length;t>this.sectionStart&&this.cbs.ontext(this.sectionStart,t),this.state=3,this.sectionStart=t}else this.delimiterIndex++;else this.inRCDATA?(this.state=32,this.stateInRCDATA(e)):(this.state=1,this.stateText(e))}stateInterpolation(e){e===this.delimiterClose[0]&&(this.state=4,this.delimiterIndex=0,this.stateInterpolationClose(e))}stateInterpolationClose(e){e===this.delimiterClose[this.delimiterIndex]?this.delimiterIndex===this.delimiterClose.length-1?(this.cbs.oninterpolation(this.sectionStart,this.index+1),this.inRCDATA?this.state=32:this.state=1,this.sectionStart=this.index+1):this.delimiterIndex++:(this.state=3,this.stateInterpolation(e))}stateSpecialStartSequence(e){let t=this.sequenceIndex===this.currentSequence.length;if(t?si(e):(32|e)===this.currentSequence[this.sequenceIndex]){if(!t)return void this.sequenceIndex++}else this.inRCDATA=!1;this.sequenceIndex=0,this.state=6,this.stateInTagName(e)}stateInRCDATA(e){if(this.sequenceIndex===this.currentSequence.length){if(e===62||mt(e)){let t=this.index-this.currentSequence.length;if(this.sectionStart<t){let i=this.index;this.index=t,this.cbs.ontext(this.sectionStart,t),this.index=i}this.sectionStart=t+2,this.stateInClosingTagName(e),this.inRCDATA=!1;return}this.sequenceIndex=0}(32|e)===this.currentSequence[this.sequenceIndex]?this.sequenceIndex+=1:this.sequenceIndex===0?this.currentSequence!==We.TitleEnd&&(this.currentSequence!==We.TextareaEnd||this.inSFCRoot)?this.fastForwardTo(60)&&(this.sequenceIndex=1):this.inVPre||e!==this.delimiterOpen[0]||(this.state=2,this.delimiterIndex=0,this.stateInterpolationOpen(e)):this.sequenceIndex=+(e===60)}stateCDATASequence(e){e===We.Cdata[this.sequenceIndex]?++this.sequenceIndex===We.Cdata.length&&(this.state=28,this.currentSequence=We.CdataEnd,this.sequenceIndex=0,this.sectionStart=this.index+1):(this.sequenceIndex=0,this.state=23,this.stateInDeclaration(e))}fastForwardTo(e){for(;++this.index<this.buffer.length;){let t=this.buffer.charCodeAt(this.index);if(t===10&&this.newlines.push(this.index),t===e)return!0}return this.index=this.buffer.length-1,!1}stateInCommentLike(e){e===this.currentSequence[this.sequenceIndex]?++this.sequenceIndex===this.currentSequence.length&&(this.currentSequence===We.CdataEnd?this.cbs.oncdata(this.sectionStart,this.index-2):this.cbs.oncomment(this.sectionStart,this.index-2),this.sequenceIndex=0,this.sectionStart=this.index+1,this.state=1):this.sequenceIndex===0?this.fastForwardTo(this.currentSequence[0])&&(this.sequenceIndex=1):e!==this.currentSequence[this.sequenceIndex-1]&&(this.sequenceIndex=0)}startSpecial(e,t){this.enterRCDATA(e,t),this.state=31}enterRCDATA(e,t){this.inRCDATA=!0,this.currentSequence=e,this.sequenceIndex=t}stateBeforeTagName(e){e===33?(this.state=22,this.sectionStart=this.index+1):e===63?(this.state=24,this.sectionStart=this.index+1):ao(e)?(this.sectionStart=this.index,this.mode===0?this.state=6:this.inSFCRoot?this.state=34:this.inXML?this.state=6:e===116?this.state=30:this.state=e===115?29:6):e===47?this.state=8:(this.state=1,this.stateText(e))}stateInTagName(e){si(e)&&this.handleTagName(e)}stateInSFCRootTagName(e){if(si(e)){let t=this.buffer.slice(this.sectionStart,this.index);t!=="template"&&this.enterRCDATA(Xn("</"+t),0),this.handleTagName(e)}}handleTagName(e){this.cbs.onopentagname(this.sectionStart,this.index),this.sectionStart=-1,this.state=11,this.stateBeforeAttrName(e)}stateBeforeClosingTagName(e){mt(e)||(e===62?(this.state=1,this.sectionStart=this.index+1):(this.state=ao(e)?9:27,this.sectionStart=this.index))}stateInClosingTagName(e){(e===62||mt(e))&&(this.cbs.onclosetag(this.sectionStart,this.index),this.sectionStart=-1,this.state=10,this.stateAfterClosingTagName(e))}stateAfterClosingTagName(e){e===62&&(this.state=1,this.sectionStart=this.index+1)}stateBeforeAttrName(e){e===62?(this.cbs.onopentagend(this.index),this.inRCDATA?this.state=32:this.state=1,this.sectionStart=this.index+1):e===47?this.state=7:e===60&&this.peek()===47?(this.cbs.onopentagend(this.index),this.state=5,this.sectionStart=this.index):mt(e)||this.handleAttrStart(e)}handleAttrStart(e){e===118&&this.peek()===45?(this.state=13,this.sectionStart=this.index):e===46||e===58||e===64||e===35?(this.cbs.ondirname(this.index,this.index+1),this.state=14,this.sectionStart=this.index+1):(this.state=12,this.sectionStart=this.index)}stateInSelfClosingTag(e){e===62?(this.cbs.onselfclosingtag(this.index),this.state=1,this.sectionStart=this.index+1,this.inRCDATA=!1):mt(e)||(this.state=11,this.stateBeforeAttrName(e))}stateInAttrName(e){(e===61||si(e))&&(this.cbs.onattribname(this.sectionStart,this.index),this.handleAttrNameEnd(e))}stateInDirName(e){e===61||si(e)?(this.cbs.ondirname(this.sectionStart,this.index),this.handleAttrNameEnd(e)):e===58?(this.cbs.ondirname(this.sectionStart,this.index),this.state=14,this.sectionStart=this.index+1):e===46&&(this.cbs.ondirname(this.sectionStart,this.index),this.state=16,this.sectionStart=this.index+1)}stateInDirArg(e){e===61||si(e)?(this.cbs.ondirarg(this.sectionStart,this.index),this.handleAttrNameEnd(e)):e===91?this.state=15:e===46&&(this.cbs.ondirarg(this.sectionStart,this.index),this.state=16,this.sectionStart=this.index+1)}stateInDynamicDirArg(e){e===93?this.state=14:(e===61||si(e))&&(this.cbs.ondirarg(this.sectionStart,this.index+1),this.handleAttrNameEnd(e))}stateInDirModifier(e){e===61||si(e)?(this.cbs.ondirmodifier(this.sectionStart,this.index),this.handleAttrNameEnd(e)):e===46&&(this.cbs.ondirmodifier(this.sectionStart,this.index),this.sectionStart=this.index+1)}handleAttrNameEnd(e){this.sectionStart=this.index,this.state=17,this.cbs.onattribnameend(this.index),this.stateAfterAttrName(e)}stateAfterAttrName(e){e===61?this.state=18:e===47||e===62?(this.cbs.onattribend(0,this.sectionStart),this.sectionStart=-1,this.state=11,this.stateBeforeAttrName(e)):mt(e)||(this.cbs.onattribend(0,this.sectionStart),this.handleAttrStart(e))}stateBeforeAttrValue(e){e===34?(this.state=19,this.sectionStart=this.index+1):e===39?(this.state=20,this.sectionStart=this.index+1):mt(e)||(this.sectionStart=this.index,this.state=21,this.stateInAttrValueNoQuotes(e))}handleInAttrValue(e,t){(e===t||this.fastForwardTo(t))&&(this.cbs.onattribdata(this.sectionStart,this.index),this.sectionStart=-1,this.cbs.onattribend(t===34?3:2,this.index+1),this.state=11)}stateInAttrValueDoubleQuotes(e){this.handleInAttrValue(e,34)}stateInAttrValueSingleQuotes(e){this.handleInAttrValue(e,39)}stateInAttrValueNoQuotes(e){mt(e)||e===62?(this.cbs.onattribdata(this.sectionStart,this.index),this.sectionStart=-1,this.cbs.onattribend(1,this.index),this.state=11,this.stateBeforeAttrName(e)):(e===39||e===60||e===61||e===96)&&this.cbs.onerr(18,this.index)}stateBeforeDeclaration(e){e===91?(this.state=26,this.sequenceIndex=0):this.state=e===45?25:23}stateInDeclaration(e){(e===62||this.fastForwardTo(62))&&(this.state=1,this.sectionStart=this.index+1)}stateInProcessingInstruction(e){(e===62||this.fastForwardTo(62))&&(this.cbs.onprocessinginstruction(this.sectionStart,this.index),this.state=1,this.sectionStart=this.index+1)}stateBeforeComment(e){e===45?(this.state=28,this.currentSequence=We.CommentEnd,this.sequenceIndex=2,this.sectionStart=this.index+1):this.state=23}stateInSpecialComment(e){(e===62||this.fastForwardTo(62))&&(this.cbs.oncomment(this.sectionStart,this.index),this.state=1,this.sectionStart=this.index+1)}stateBeforeSpecialS(e){e===We.ScriptEnd[3]?this.startSpecial(We.ScriptEnd,4):e===We.StyleEnd[3]?this.startSpecial(We.StyleEnd,4):(this.state=6,this.stateInTagName(e))}stateBeforeSpecialT(e){e===We.TitleEnd[3]?this.startSpecial(We.TitleEnd,4):e===We.TextareaEnd[3]?this.startSpecial(We.TextareaEnd,4):(this.state=6,this.stateInTagName(e))}startEntity(){}stateInEntity(){}parse(e){for(this.buffer=e;this.index<this.buffer.length;){let t=this.buffer.charCodeAt(this.index);switch(t===10&&this.state!==33&&this.newlines.push(this.index),this.state){case 1:this.stateText(t);break;case 2:this.stateInterpolationOpen(t);break;case 3:this.stateInterpolation(t);break;case 4:this.stateInterpolationClose(t);break;case 31:this.stateSpecialStartSequence(t);break;case 32:this.stateInRCDATA(t);break;case 26:this.stateCDATASequence(t);break;case 19:this.stateInAttrValueDoubleQuotes(t);break;case 12:this.stateInAttrName(t);break;case 13:this.stateInDirName(t);break;case 14:this.stateInDirArg(t);break;case 15:this.stateInDynamicDirArg(t);break;case 16:this.stateInDirModifier(t);break;case 28:this.stateInCommentLike(t);break;case 27:this.stateInSpecialComment(t);break;case 11:this.stateBeforeAttrName(t);break;case 6:this.stateInTagName(t);break;case 34:this.stateInSFCRootTagName(t);break;case 9:this.stateInClosingTagName(t);break;case 5:this.stateBeforeTagName(t);break;case 17:this.stateAfterAttrName(t);break;case 20:this.stateInAttrValueSingleQuotes(t);break;case 18:this.stateBeforeAttrValue(t);break;case 8:this.stateBeforeClosingTagName(t);break;case 10:this.stateAfterClosingTagName(t);break;case 29:this.stateBeforeSpecialS(t);break;case 30:this.stateBeforeSpecialT(t);break;case 21:this.stateInAttrValueNoQuotes(t);break;case 7:this.stateInSelfClosingTag(t);break;case 23:this.stateInDeclaration(t);break;case 22:this.stateBeforeDeclaration(t);break;case 25:this.stateBeforeComment(t);break;case 24:this.stateInProcessingInstruction(t);break;case 33:this.stateInEntity()}this.index++}this.cleanup(),this.finish()}cleanup(){this.sectionStart!==this.index&&(this.state===1||this.state===32&&this.sequenceIndex===0?(this.cbs.ontext(this.sectionStart,this.index),this.sectionStart=this.index):(this.state===19||this.state===20||this.state===21)&&(this.cbs.onattribdata(this.sectionStart,this.index),this.sectionStart=this.index))}finish(){this.handleTrailingData(),this.cbs.onend()}handleTrailingData(){let e=this.buffer.length;this.sectionStart>=e||(this.state===28?this.currentSequence===We.CdataEnd?this.cbs.oncdata(this.sectionStart,e):this.cbs.oncomment(this.sectionStart,e):this.state===6||this.state===11||this.state===18||this.state===17||this.state===12||this.state===13||this.state===14||this.state===15||this.state===16||this.state===20||this.state===19||this.state===21||this.state===9||this.cbs.ontext(this.sectionStart,e))}emitCodePoint(e,t){}}(qe,{onerr:po,ontext(e,t){gn(Je(e,t),e,t)},ontextentity(e,t,i){gn(e,t,i)},oninterpolation(e,t){if(wi)return gn(Je(e,t),e,t);let i=e+Oe.delimiterOpen.length,s=t-Oe.delimiterClose.length;for(;mt(Wt.charCodeAt(i));)i++;for(;mt(Wt.charCodeAt(s-1));)s--;let n=Je(i,s);n.includes("&")&&(n=we.decodeEntities(n,!1)),Sa({type:5,content:bn(n,!1,Ee(i,s)),loc:Ee(e,t)})},onopentagname(e,t){let i=Je(e,t);Ge={type:1,tag:i,ns:we.getNamespace(i,qe[0],we.ns),tagType:0,props:[],children:[],loc:Ee(e-1,t),codegenNode:void 0}},onopentagend(e){co(e)},onclosetag(e,t){let i=Je(e,t);if(!we.isVoidTag(i)){let s=!1;for(let n=0;n<qe.length;n++)if(qe[n].tag.toLowerCase()===i.toLowerCase()){s=!0,n>0&&qe[0].loc.start.offset;for(let r=0;r<=n;r++)qn(qe.shift(),t,r<n);break}s||Cd(e,60)}},onselfclosingtag(e){let t=Ge.tag;Ge.isSelfClosing=!0,co(e),qe[0]&&qe[0].tag===t&&qn(qe.shift(),e)},onattribname(e,t){ve={type:6,name:Je(e,t),nameLoc:Ee(e,t),value:void 0,loc:Ee(e)}},ondirname(e,t){let i=Je(e,t),s=i==="."||i===":"?"bind":i==="@"?"on":i==="#"?"slot":i.slice(2);if(wi||s==="")ve={type:6,name:i,nameLoc:Ee(e,t),value:void 0,loc:Ee(e)};else if(ve={type:7,name:s,rawName:i,exp:void 0,arg:void 0,modifiers:i==="."?[oe("prop")]:[],loc:Ee(e)},s==="pre"){wi=Oe.inVPre=!0,_a=Ge;let n=Ge.props;for(let r=0;r<n.length;r++)n[r].type===7&&(n[r]=function(a){let l={type:6,name:a.rawName,nameLoc:Ee(a.loc.start.offset,a.loc.start.offset+a.rawName.length),value:void 0,loc:a.loc};if(a.exp){let o=a.exp.loc;o.end.offset<a.loc.end.offset&&(o.start.offset--,o.start.column--,o.end.offset++,o.end.column++),l.value={type:2,content:a.exp.content,loc:o}}return l}(n[r]))}},ondirarg(e,t){if(e===t)return;let i=Je(e,t);if(wi&&!lo(ve))ve.name+=i,ki(ve.nameLoc,t);else{let s=i[0]!=="[";ve.arg=bn(s?i:i.slice(1,-1),s,Ee(e,t),3*!!s)}},ondirmodifier(e,t){let i=Je(e,t);if(wi&&!lo(ve))ve.name+="."+i,ki(ve.nameLoc,t);else if(ve.name==="slot"){let s=ve.arg;s&&(s.content+="."+i,ki(s.loc,t))}else{let s=oe(i,!0,Ee(e,t));ve.modifiers.push(s)}},onattribdata(e,t){ht+=Je(e,t),Ft<0&&(Ft=e),xi=t},onattribentity(e,t,i){ht+=e,Ft<0&&(Ft=t),xi=i},onattribnameend(e){let t=Je(ve.loc.start.offset,e);ve.type===7&&(ve.rawName=t),Ge.props.some(i=>(i.type===7?i.rawName:i.name)===t)},onattribend(e,t){Ge&&ve&&(ki(ve.loc,t),e!==0&&(ht.includes("&")&&(ht=we.decodeEntities(ht,!0)),ve.type===6?(ve.name==="class"&&(ht=Ad(ht).trim()),ve.value={type:2,content:ht,loc:e===1?Ee(Ft,xi):Ee(Ft-1,xi+1)},Oe.inSFCRoot&&Ge.tag==="template"&&ve.name==="lang"&&ht&&ht!=="html"&&Oe.enterRCDATA(Xn("</template"),0)):(ve.exp=bn(ht,!1,Ee(Ft,xi),0,0),ve.name==="for"&&(ve.forParseResult=function(i){let s=i.loc,n=i.content,r=n.match(im);if(!r)return;let[,a,l]=r,o=(y,m,x=!1)=>{let q=s.start.offset+m,b=q+y.length;return bn(y,!1,Ee(q,b),0,+!!x)},c={source:o(l.trim(),n.indexOf(l,a.length)),value:void 0,key:void 0,index:void 0,finalized:!1},d=a.trim().replace(sm,"").trim(),p=a.indexOf(d),f=d.match(oo);if(f){let y;d=d.replace(oo,"").trim();let m=f[1].trim();if(m&&(y=n.indexOf(m,p+d.length),c.key=o(m,y,!0)),f[2]){let x=f[2].trim();x&&(c.index=o(x,n.indexOf(x,c.key?y+m.length:p+d.length),!0))}}return d&&(c.value=o(d,p,!0)),c}(ve.exp)))),(ve.type!==7||ve.name!=="pre")&&Ge.props.push(ve)),ht="",Ft=xi=-1},oncomment(e,t){we.comments&&Sa({type:3,content:Je(e,t),loc:Ee(e-4,t+3)})},onend(){let e=Wt.length;for(let t=0;t<qe.length;t++)qn(qe[t],e-1),qe[t].loc.start.offset},oncdata(e,t){(qe[0]?qe[0].ns:we.ns)!==0&&gn(Je(e,t),e,t)},onprocessinginstruction(e){(qe[0]?qe[0].ns:we.ns)===0&&po(21,e-1)}}),oo=/,([^,\}\]]*)(?:,([^,\}\]]*))?$/,sm=/^\(|\)$/g;function Je(e,t){return Wt.slice(e,t)}function co(e){Oe.inSFCRoot&&(Ge.innerLoc=Ee(e+1,e+1)),Sa(Ge);let{tag:t,ns:i}=Ge;i===0&&we.isPreTag(t)&&hl++,we.isVoidTag(t)?qn(Ge,e):(qe.unshift(Ge),(i===1||i===2)&&(Oe.inXML=!0)),Ge=null}function gn(e,t,i){{let r=qe[0]&&qe[0].tag;r!=="script"&&r!=="style"&&e.includes("&")&&(e=we.decodeEntities(e,!1))}let s=qe[0]||ir,n=s.children[s.children.length-1];n&&n.type===2?(n.content+=e,ki(n.loc,i)):s.children.push({type:2,content:e,loc:Ee(t,i)})}function qn(e,t,i=!1){i?ki(e.loc,Cd(t,60)):ki(e.loc,function(a){let l=a;for(;Wt.charCodeAt(l)!==62&&l<Wt.length-1;)l++;return l}(t)+1),Oe.inSFCRoot&&(e.children.length?e.innerLoc.end=de({},e.children[e.children.length-1].loc.end):e.innerLoc.end=de({},e.innerLoc.start),e.innerLoc.source=Je(e.innerLoc.start.offset,e.innerLoc.end.offset));let{tag:s,ns:n,children:r}=e;if(!wi&&(s==="slot"?e.tagType=2:function({tag:a,props:l}){if(a==="template"){for(let o=0;o<l.length;o++)if(l[o].type===7&&nm.has(l[o].name))return!0}return!1}(e)?e.tagType=3:function({tag:a,props:l}){var o;if(we.isCustomElement(a))return!1;if(a==="component"||(o=a.charCodeAt(0))>64&&o<91||xd(a)||we.isBuiltInComponent&&we.isBuiltInComponent(a)||we.isNativeTag&&!we.isNativeTag(a))return!0;for(let c=0;c<l.length;c++){let d=l[c];if(d.type===6&&d.name==="is"&&d.value&&d.value.content.startsWith("vue:"))return!0}return!1}(e)&&(e.tagType=1)),Oe.inRCDATA||(e.children=Md(r)),n===0&&we.isIgnoreNewlineTag(s)){let a=r[0];a&&a.type===2&&(a.content=a.content.replace(/^\r?\n/,""))}n===0&&we.isPreTag(s)&&hl--,_a===e&&(wi=Oe.inVPre=!1,_a=null),Oe.inXML&&(qe[0]?qe[0].ns:we.ns)===0&&(Oe.inXML=!1)}function Cd(e,t){let i=e;for(;Wt.charCodeAt(i)!==t&&i>=0;)i--;return i}var nm=new Set(["if","else","else-if","for","slot"]),rm=/\r\n/g;function Md(e){let t=we.whitespace!=="preserve",i=!1;for(let s=0;s<e.length;s++){let n=e[s];if(n.type===2)if(hl)n.content=n.content.replace(rm,`
`);else if(Sd(n.content)){let r=e[s-1]&&e[s-1].type,a=e[s+1]&&e[s+1].type;!r||!a||t&&(r===3&&(a===3||a===1)||r===1&&(a===3||a===1&&function(l){for(let o=0;o<l.length;o++){let c=l.charCodeAt(o);if(c===10||c===13)return!0}return!1}(n.content)))?(i=!0,e[s]=null):n.content=" "}else t&&(n.content=Ad(n.content))}return i?e.filter(Boolean):e}function Ad(e){let t="",i=!1;for(let s=0;s<e.length;s++)mt(e.charCodeAt(s))?i||(t+=" ",i=!0):(t+=e[s],i=!1);return t}function Sa(e){(qe[0]||ir).children.push(e)}function Ee(e,t){return{start:Oe.getPos(e),end:t==null?t:Oe.getPos(t),source:t==null?t:Je(e,t)}}function ki(e,t){e.end=Oe.getPos(t),e.source=Je(e.start.offset,t)}function bn(e,t=!1,i,s=0,n=0){return oe(e,t,i,s)}function po(e,t,i){we.onError(be(e,Ee(t,t)))}function uo(e){let t=e.children.filter(i=>i.type!==3);return t.length!==1||t[0].type!==1||er(t[0])?null:t[0]}function ft(e,t){let{constantCache:i}=t;switch(e.type){case 1:if(e.tagType!==0)return 0;let l=i.get(e);if(l!==void 0)return l;let o=e.codegenNode;if(o.type!==13||o.isBlock&&e.tag!=="svg"&&e.tag!=="foreignObject"&&e.tag!=="math")return 0;if(o.patchFlag!==void 0)return i.set(e,0),0;{let d=3,p=Id(e,t);if(p===0)return i.set(e,0),0;p<d&&(d=p);for(let f=0;f<e.children.length;f++){let y=ft(e.children[f],t);if(y===0)return i.set(e,0),0;y<d&&(d=y)}if(d>1)for(let f=0;f<e.props.length;f++){let y=e.props[f];if(y.type===7&&y.name==="bind"&&y.exp){let m=ft(y.exp,t);if(m===0)return i.set(e,0),0;m<d&&(d=m)}}if(o.isBlock){var s,n,r,a;for(let f=0;f<e.props.length;f++)if(e.props[f].type===7)return i.set(e,0),0;t.removeHelper(Ni),t.removeHelper((s=t.inSSR,n=o.isComponent,s||n?Ei:Oi)),o.isBlock=!1,t.helper((r=t.inSSR,a=o.isComponent,r||a?di:pi))}return i.set(e,d),d}case 2:case 3:return 3;case 9:case 11:case 10:default:return 0;case 5:case 12:return ft(e.content,t);case 4:return e.constType;case 8:let c=3;for(let d=0;d<e.children.length;d++){let p=e.children[d];if(re(p)||Ze(p))continue;let f=ft(p,t);if(f===0)return 0;f<c&&(c=f)}return c;case 20:return 2}}var am=new Set([al,ll,$s,en]);function Id(e,t){let i=3,s=Nd(e);if(s&&s.type===15){let{properties:n}=s;for(let r=0;r<n.length;r++){let a,{key:l,value:o}=n[r],c=ft(l,t);if(c===0)return c;if(c<i&&(i=c),(a=o.type===4?ft(o,t):o.type===14?function d(p,f){if(p.type===14&&!re(p.callee)&&am.has(p.callee)){let y=p.arguments[0];if(y.type===4)return ft(y,f);if(y.type===14)return d(y,f)}return 0}(o,t):0)===0)return a;a<i&&(i=a)}}return i}function Nd(e){let t=e.codegenNode;if(t.type===13)return t.props}function sr(e,t){t.currentNode=e;let{nodeTransforms:i}=t,s=[];for(let a=0;a<i.length;a++){let l=i[a](e,t);if(l&&(G(l)?s.push(...l):s.push(l)),!t.currentNode)return;e=t.currentNode}switch(e.type){case 3:t.ssr||t.helper(Zs);break;case 5:t.ssr||t.helper(wr);break;case 9:for(let o=0;o<e.branches.length;o++)sr(e.branches[o],t);break;case 10:case 11:case 1:case 0:var n=e;let a=0,l=()=>{a--};for(;a<n.children.length;a++){let o=n.children[a];re(o)||(t.grandParent=t.parent,t.parent=n,t.childIndex=a,t.onNodeRemoved=l,sr(o,t))}}t.currentNode=e;let r=s.length;for(;r--;)s[r]()}function Ed(e,t){let i=re(e)?s=>s===e:s=>e.test(s);return(s,n)=>{if(s.type===1){let{props:r}=s;if(s.tagType===3&&r.some(em))return;let a=[];for(let l=0;l<r.length;l++){let o=r[l];if(o.type===7&&i(o.name)){r.splice(l,1),l--;let c=t(s,o,n);c&&a.push(c)}}return a}}}var yn="/*@__PURE__*/",ho=e=>`${rs[e]}: _${rs[e]}`;function mo(e,t,{helper:i,push:s,newline:n,isTS:r}){let a=i(t==="component"?il:sl);for(let l=0;l<e.length;l++){let o=e[l],c=o.endsWith("__self");c&&(o=o.slice(0,-6)),s(`const ${ka(o,t)} = ${a}(${JSON.stringify(o)}${c?", true":""})${r?"!":""}`),l<e.length-1&&n()}}function qa(e,t){let i=e.length>3;t.push("["),i&&t.indent(),ks(e,t,i),i&&t.deindent(),t.push("]")}function ks(e,t,i=!1,s=!0){let{push:n,newline:r}=t;for(let a=0;a<e.length;a++){let l=e[a];re(l)?n(l,-3):G(l)?qa(l,t):st(l,t),a<e.length-1&&(i?(s&&n(","),r()):s&&n(", "))}}function st(e,t){var i,s,n;if(re(e))return void t.push(e,-3);if(Ze(e))return void t.push(t.helper(e));switch(e.type){case 1:case 9:case 11:case 12:st(e.codegenNode,t);break;case 2:i=e,t.push(JSON.stringify(i.content),-3,i);break;case 4:fo(e,t);break;case 5:(function(r,a){let{push:l,helper:o,pure:c}=a;c&&l(yn),l(`${o(wr)}(`),st(r.content,a),l(")")})(e,t);break;case 8:vo(e,t);break;case 3:(function(r,a){let{push:l,helper:o,pure:c}=a;c&&l(yn),l(`${o(Zs)}(${JSON.stringify(r.content)})`,-3,r)})(e,t);break;case 13:(function(r,a){var l,o;let c,{push:d,helper:p,pure:f}=a,{tag:y,props:m,children:x,patchFlag:q,dynamicProps:b,directives:u,isBlock:h,disableTracking:g,isComponent:_}=r;q&&(c=String(q)),u&&d(p(nl)+"("),h&&d(`(${p(Ni)}(${g?"true":""}), `),f&&d(yn),d(p(h?(l=a.inSSR,l||_?Ei:Oi):(o=a.inSSR,o||_?di:pi))+"(",-2,r),ks(function(k){let S=k.length;for(;S--&&k[S]==null;);return k.slice(0,S+1).map(C=>C||"null")}([y,m,x,c,b]),a),d(")"),h&&d(")"),u&&(d(", "),st(u,a),d(")"))})(e,t);break;case 14:(function(r,a){let{push:l,helper:o,pure:c}=a,d=re(r.callee)?r.callee:o(r.callee);c&&l(yn),l(d+"(",-2,r),ks(r.arguments,a),l(")")})(e,t);break;case 15:(function(r,a){let{push:l,indent:o,deindent:c,newline:d}=a,{properties:p}=r;if(!p.length)return l("{}",-2,r);let f=p.length>1;l(f?"{":"{ "),f&&o();for(let y=0;y<p.length;y++){let{key:m,value:x}=p[y];(function(q,b){let{push:u}=b;if(q.type===8)u("["),vo(q,b),u("]");else if(q.isStatic){let h;u((h=q.content,xa.test(h)?JSON.stringify(q.content):q.content),-2,q)}else u(`[${q.content}]`,-3,q)})(m,a),l(": "),st(x,a),y<p.length-1&&(l(","),d())}f&&c(),l(f?"}":" }")})(e,t);break;case 17:s=e,n=t,qa(s.elements,n);break;case 18:(function(r,a){let{push:l,indent:o,deindent:c}=a,{params:d,returns:p,body:f,newline:y,isSlot:m}=r;m&&l(`_${rs[cl]}(`),l("(",-2,r),G(d)?ks(d,a):d&&st(d,a),l(") => "),(y||f)&&(l("{"),o()),p?(y&&l("return "),G(p)?qa(p,a):st(p,a)):f&&st(f,a),(y||f)&&(c(),l("}")),m&&l(")")})(e,t);break;case 19:(function(r,a){let{test:l,consequent:o,alternate:c,newline:d}=r,{push:p,indent:f,deindent:y,newline:m}=a;if(l.type===4){let q,b=(q=l.content,!!xa.test(q));b&&p("("),fo(l,a),b&&p(")")}else p("("),st(l,a),p(")");d&&f(),a.indentLevel++,d||p(" "),p("? "),st(o,a),a.indentLevel--,d&&m(),d||p(" "),p(": ");let x=c.type===19;!x&&a.indentLevel++,st(c,a),!x&&a.indentLevel--,d&&y(!0)})(e,t);break;case 20:(function(r,a){let{push:l,helper:o,indent:c,deindent:d,newline:p}=a,{needPauseTracking:f,needArraySpread:y}=r;y&&l("[...("),l(`_cache[${r.index}] || (`),f&&(c(),l(`${o(Yn)}(-1`),r.inVOnce&&l(", true"),l("),"),p(),l("(")),l(`_cache[${r.index}] = `),st(r.value,a),f&&(l(`).cacheIndex = ${r.index},`),p(),l(`${o(Yn)}(1),`),p(),l(`_cache[${r.index}]`),d()),l(")"),y&&l(")]")})(e,t);break;case 21:ks(e.body,t,!0,!1)}}function fo(e,t){let{content:i,isStatic:s}=e;t.push(s?JSON.stringify(i):i,-3,e)}function vo(e,t){for(let i=0;i<e.children.length;i++){let s=e.children[i];re(s)?t.push(s,-3):st(s,t)}}var lm=Ed(/^(?:if|else|else-if)$/,(e,t,i)=>function(s,n,r,a){if(n.name!=="else"&&(!n.exp||!n.exp.content.trim())){let o=n.exp?n.exp.loc:s.loc;r.onError(be(28,n.loc)),n.exp=oe("true",!1,o)}if(n.name==="if"){var l;let o=go(s,n),c={type:9,loc:Ee((l=s.loc).start.offset,l.end.offset),branches:[o]};if(r.replaceNode(c),a)return a(c,o,!0)}else{let o=r.parent.children,c=o.indexOf(s);for(;c-->=-1;){let d=o[c];if(d&&qd(d)){r.removeNode(d);continue}if(d&&d.type===9){(n.name==="else-if"||n.name==="else")&&d.branches[d.branches.length-1].condition===void 0&&r.onError(be(30,s.loc)),r.removeNode();let p=go(s,n);d.branches.push(p);let f=a&&a(d,p,!1);sr(p,r),f&&f(),r.currentNode=null}else r.onError(be(30,s.loc));break}}}(e,t,i,(s,n,r)=>{let a=i.parent.children,l=a.indexOf(s),o=0;for(;l-->=0;){let c=a[l];c&&c.type===9&&(o+=c.branches.length)}return()=>{r?s.codegenNode=bo(n,o,i):function(c){for(;;)if(c.type===19){if(c.alternate.type!==19)return c;c=c.alternate}else c.type===20&&(c=c.value)}(s.codegenNode).alternate=bo(n,o+s.branches.length-1,i)}}));function go(e,t){let i=e.tagType===3;return{type:10,loc:e.loc,condition:t.name==="else"?void 0:t.exp,children:i&&!_t(e,"for")?e.children:[e],userKey:kr(e,"key"),isTemplateIf:i}}function bo(e,t,i){return e.condition?ba(e.condition,yo(e,t,i),ze(i.helper(Zs),['""',"true"])):yo(e,t,i)}function yo(e,t,i){let{helper:s}=i,n=je("key",oe(`${t}`,!1,gt,2)),{children:r}=e,a=r[0];if(r.length!==1||a.type!==1){if(r.length!==1||a.type!==11)return Us(i,s(Ds),St([n]),r,64,void 0,void 0,!0,!1,!1,e.loc);{let l=a.codegenNode;return tr(l,n,i),l}}{let l=a.codegenNode,o=l.type===14&&l.callee===dl?l.arguments[1].returns:l;return o.type===13&&pl(o,i),tr(o,n,i),l}}var om=Ed("for",(e,t,i)=>{let{helper:s,removeHelper:n}=i;return function(r,a,l,o){if(!a.exp)return void l.onError(be(31,a.loc));let c=a.forParseResult;if(!c)return void l.onError(be(32,a.loc));Od(c);let{scopes:d}=l,{source:p,value:f,key:y,index:m}=c,x={type:11,loc:a.loc,source:p,valueAlias:f,keyAlias:y,objectIndexAlias:m,parseResult:c,children:Zn(r)?r.children:[r]};l.replaceNode(x),d.vFor++;let q=o&&o(x);return()=>{d.vFor--,q&&q()}}(e,t,i,r=>{let a=ze(s(rl),[r.source]),l=Zn(e),o=_t(e,"memo"),c=kr(e,"key",!1,!0);c&&c.type;let d=c&&(c.type===6?c.value?oe(c.value.content,!0):void 0:c.exp),p=d?je("key",d):null,f=r.source.type===4&&r.source.constType>0,y=f?64:c?128:256;return r.codegenNode=Us(i,s(Ds),void 0,a,y,void 0,void 0,!0,!f,!1,e.loc),()=>{let m,{children:x}=r,q=x.length!==1||x[0].type!==1,b=er(e)?e:l&&e.children.length===1&&er(e.children[0])?e.children[0]:null;if(b)m=b.codegenNode,l&&p&&tr(m,p,i);else if(q)m=Us(i,s(Ds),p?St([p]):void 0,e.children,64,void 0,void 0,!0,void 0,!1);else{var u,h,g,_,k,S,C,E;m=x[0].codegenNode,l&&p&&tr(m,p,i),!f!==m.isBlock&&(m.isBlock?(n(Ni),n((u=i.inSSR,h=m.isComponent,u||h?Ei:Oi))):n((g=i.inSSR,_=m.isComponent,g||_?di:pi))),m.isBlock=!f,m.isBlock?(s(Ni),s((k=i.inSSR,S=m.isComponent,k||S?Ei:Oi))):s((C=i.inSSR,E=m.isComponent,C||E?di:pi))}if(o){let O=as(Ta(r.parseResult,[oe("_cached")]));O.body={type:21,body:[At(["const _memo = (",o.exp,")"]),At(["if (_cached && _cached.el",...d?[" && _cached.key === ",d]:[],` && ${i.helperString(bd)}(_cached, _memo)) return _cached`]),At(["const _item = ",m]),oe("_item.memo = _memo"),oe("return _item")],loc:gt},a.arguments.push(O,oe("_cache"),oe(String(i.cached.length))),i.cached.push(null)}else a.arguments.push(as(Ta(r.parseResult),m,!0))}})});function Od(e,t){e.finalized||(e.finalized=!0)}function Ta({value:e,key:t,index:i},s=[]){var n=[e,t,i,...s];let r=n.length;for(;r--&&!n[r];);return n.slice(0,r+1).map((a,l)=>a||oe("_".repeat(l+1),!1))}var xo=oe("undefined",!1),cm=(e,t)=>{if(e.type===1&&(e.tagType===1||e.tagType===3)){let i=_t(e,"slot");if(i)return i.exp,t.scopes.vSlot++,()=>{t.scopes.vSlot--}}};function xn(e,t,i){let s=[je("name",e),je("fn",t)];return i!=null&&s.push(je("key",oe(String(i),!0))),St(s)}var Rd=new WeakMap,dm=(e,t)=>function(){let i,s,n,r,a;if((e=t.currentNode).type!==1||e.tagType!==0&&e.tagType!==1)return;let{tag:l,props:o}=e,c=e.tagType===1,d=c?function(m,x,q=!1){let{tag:b}=m,u=Ca(b),h=kr(m,"is",!1,!0);if(h)if(u){let _;if(h.type===6?_=h.value&&oe(h.value.content,!0):(_=h.exp)||(_=oe("is",!1,h.arg.loc)),_)return ze(x.helper(fa),[_])}else h.type===6&&h.value.content.startsWith("vue:")&&(b=h.value.content.slice(4));let g=xd(b)||x.isBuiltInComponent(b);return g?(q||x.helper(g),g):(x.helper(il),x.components.add(b),ka(b,"component"))}(e,t):`"${l}"`,p=me(d)&&d.callee===fa,f=0,y=p||d===Is||d===el||!c&&(l==="svg"||l==="foreignObject"||l==="math");if(o.length>0){let m=Pd(e,t,void 0,c,p);i=m.props,f=m.patchFlag,r=m.dynamicPropNames;let x=m.directives;a=x&&x.length?Ci(x.map(q=>function(b,u){let h=[],g=Rd.get(b);g?h.push(u.helperString(g)):(u.helper(sl),u.directives.add(b.name),h.push(ka(b.name,"directive")));let{loc:_}=b;if(b.exp&&h.push(b.exp),b.arg&&(b.exp||h.push("void 0"),h.push(b.arg)),Object.keys(b.modifiers).length){b.arg||(b.exp||h.push("void 0"),h.push("void 0"));let k=oe("true",!1,_);h.push(St(b.modifiers.map(S=>je(S,k)),_))}return Ci(h,b.loc)}(q,t))):void 0,m.shouldUseBlock&&(y=!0)}if(e.children.length>0)if(d===Jn&&(y=!0,f|=1024),c&&d!==Is&&d!==Jn){let{slots:m,hasDynamicSlots:x}=function(q,b,u=(h,g,_,k)=>as(h,_,!1,!0,_.length?_[0].loc:k)){b.helper(cl);let{children:h,loc:g}=q,_=[],k=[],S=b.scopes.vSlot>0||b.scopes.vFor>0,C=_t(q,"slot",!0);if(C){let{arg:Q,exp:V}=C;Q&&!pt(Q)&&(S=!0),_.push(je(Q||oe("default",!0),u(V,void 0,h,g)))}let E=!1,O=!1,B=[],T=new Set,F=0;for(let Q=0;Q<h.length;Q++){let V,J,K,te,ne=h[Q];if(!Zn(ne)||!(V=_t(ne,"slot",!0))){ne.type!==3&&B.push(ne);continue}if(C){b.onError(be(37,V.loc));break}E=!0;let{children:he,loc:Ae}=ne,{arg:_e=oe("default",!0),exp:Ve,loc:et}=V;pt(_e)?J=_e?_e.content:"default":S=!0;let ce=_t(ne,"for"),ae=u(Ve,ce,he,Ae);if(K=_t(ne,"if"))S=!0,k.push(ba(K.exp,xn(_e,ae,F++),xo));else if(te=_t(ne,/^else(?:-if)?$/,!0)){let xe,Se=Q;for(;Se--&&qd(xe=h[Se]););if(xe&&Zn(xe)&&_t(xe,/^(?:else-)?if$/)){let v=k[k.length-1];for(;v.alternate.type===19;)v=v.alternate;v.alternate=te.exp?ba(te.exp,xn(_e,ae,F++),xo):xn(_e,ae,F++)}else b.onError(be(30,te.loc))}else if(ce){S=!0;let xe=ce.forParseResult;xe?(Od(xe),k.push(ze(b.helper(rl),[xe.source,as(Ta(xe),xn(_e,ae),!0)]))):b.onError(be(32,ce.loc))}else{if(J){if(T.has(J)){b.onError(be(38,et));continue}T.add(J),J==="default"&&(O=!0)}_.push(je(_e,ae))}}if(!C){let Q=(V,J)=>je("default",u(V,void 0,J,g));E?B.length&&!B.every(ul)&&(O?b.onError(be(39,B[0].loc)):_.push(Q(void 0,B))):_.push(Q(void 0,h))}let L=S?2:function Q(V){for(let J=0;J<V.length;J++){let K=V[J];switch(K.type){case 1:if(K.tagType===2||Q(K.children))return!0;break;case 9:if(Q(K.branches))return!0;break;case 10:case 11:if(Q(K.children))return!0}}return!1}(q.children)?3:1,M=St(_.concat(je("_",oe(L+"",!1))),g);return k.length&&(M=ze(b.helper(gd),[M,Ci(k)])),{slots:M,hasDynamicSlots:S}}(e,t);s=m,x&&(f|=1024)}else if(e.children.length===1&&d!==Is){let m=e.children[0],x=m.type,q=x===5||x===8;q&&ft(m,t)===0&&(f|=1),s=q||x===2?m:e.children}else s=e.children;r&&r.length&&(n=function(m){let x="[";for(let q=0,b=m.length;q<b;q++)x+=JSON.stringify(m[q]),q<b-1&&(x+=", ");return x+"]"}(r)),e.codegenNode=Us(t,d,i,s,f===0?void 0:f,n,a,!!y,!1,c,e.loc)};function Pd(e,t,i=e.props,s,n,r=!1){let a,{tag:l,loc:o,children:c}=e,d=[],p=[],f=[],y=c.length>0,m=!1,x=0,q=!1,b=!1,u=!1,h=!1,g=!1,_=!1,k=[],S=O=>{d.length&&(p.push(St(wo(d),o)),d=[]),O&&p.push(O)},C=()=>{t.scopes.vFor>0&&d.push(je(oe("ref_for",!0),oe("true")))},E=({key:O,value:B})=>{if(pt(O)){let T=O.content,F=Ri(T);F&&(!s||n)&&T.toLowerCase()!=="onclick"&&T!=="onUpdate:modelValue"&&!Vt(T)&&(h=!0),F&&Vt(T)&&(_=!0),F&&B.type===14&&(B=B.arguments[0]),B.type===20||(B.type===4||B.type===8)&&ft(B,t)>0||(T==="ref"?q=!0:T==="class"?b=!0:T==="style"?u=!0:T==="key"||k.includes(T)||k.push(T),s&&(T==="class"||T==="style")&&!k.includes(T)&&k.push(T))}else g=!0};for(let O=0;O<i.length;O++){let B=i[O];if(B.type===6){let{loc:T,name:F,nameLoc:L,value:M}=B;if(F==="ref"&&(q=!0,C()),F==="is"&&(Ca(l)||M&&M.content.startsWith("vue:")))continue;d.push(je(oe(F,!0,L),oe(M?M.content:"",!0,M?M.loc:T)))}else{let{name:T,arg:F,exp:L,loc:M,modifiers:Q}=B,V=T==="bind",J=T==="on";if(T==="slot"){s||t.onError(be(40,M));continue}if(T==="once"||T==="memo"||T==="is"||V&&Hi(F,"is")&&Ca(l)||J&&r)continue;if((V&&Hi(F,"key")||J&&y&&Hi(F,"vue:before-update"))&&(m=!0),V&&Hi(F,"ref")&&C(),!F&&(V||J)){g=!0,L?V?(C(),S(),p.push(L)):S({type:14,loc:M,callee:t.helper(ol),arguments:s?[L]:[L,"true"]}):t.onError(be(V?34:35,M));continue}V&&Q.some(te=>te.content==="prop")&&(x|=32);let K=t.directiveTransforms[T];if(K){let{props:te,needRuntime:ne}=K(B,e,t);r||te.forEach(E),J&&F&&!pt(F)?S(St(te,o)):d.push(...te),ne&&(f.push(B),Ze(ne)&&Rd.set(B,ne))}else!xp(T)&&(f.push(B),y&&(m=!0))}}if(p.length?(S(),a=p.length>1?ze(t.helper(Gn),p,o):p[0]):d.length&&(a=St(wo(d),o)),g?x|=16:(b&&!s&&(x|=2),u&&!s&&(x|=4),k.length&&(x|=8),h&&(x|=32)),!m&&(x===0||x===32)&&(q||_||f.length>0)&&(x|=512),!t.inSSR&&a)switch(a.type){case 15:let O=-1,B=-1,T=!1;for(let M=0;M<a.properties.length;M++){let Q=a.properties[M].key;pt(Q)?Q.content==="class"?O=M:Q.content==="style"&&(B=M):Q.isHandlerKey||(T=!0)}let F=a.properties[O],L=a.properties[B];T?a=ze(t.helper($s),[a]):(F&&!pt(F.value)&&(F.value=ze(t.helper(al),[F.value])),L&&(u||L.value.type===4&&L.value.content.trim()[0]==="["||L.value.type===17)&&(L.value=ze(t.helper(ll),[L.value])));break;case 14:break;default:a=ze(t.helper($s),[ze(t.helper(en),[a])])}return{props:a,directives:f,patchFlag:x,dynamicPropNames:k,shouldUseBlock:m}}function wo(e){let t=new Map,i=[];for(let r=0;r<e.length;r++){var s,n;let a=e[r];if(a.key.type===8||!a.key.isStatic){i.push(a);continue}let l=a.key.content,o=t.get(l);o?(l==="style"||l==="class"||Ri(l))&&(s=o,n=a,s.value.type===17?s.value.elements.push(n.value):s.value=Ci([s.value,n.value],s.loc)):(t.set(l,a),i.push(a))}return i}function Ca(e){return e==="component"||e==="Component"}var pm=(e,t)=>{if(er(e)){let{children:i,loc:s}=e,{slotName:n,slotProps:r}=function(o,c){let d,p='"default"',f=[];for(let y=0;y<o.props.length;y++){let m=o.props[y];if(m.type===6)m.value&&(m.name==="name"?p=JSON.stringify(m.value.content):(m.name=ye(m.name),f.push(m)));else if(m.name==="bind"&&Hi(m.arg,"name")){if(m.exp)p=m.exp;else if(m.arg&&m.arg.type===4){let x=ye(m.arg.content);p=m.exp=oe(x,!1,m.arg.loc)}}else m.name==="bind"&&m.arg&&pt(m.arg)&&(m.arg.content=ye(m.arg.content)),f.push(m)}if(f.length>0){let{props:y,directives:m}=Pd(o,c,f,!1,!1);d=y,m.length&&c.onError(be(36,m[0].loc))}return{slotName:p,slotProps:d}}(e,t),a=[t.prefixIdentifiers?"_ctx.$slots":"$slots",n,"{}","undefined","true"],l=2;r&&(a[2]=r,l=3),i.length&&(a[3]=as([],i,!1,!1,s),l=4),t.scopeId&&!t.slotted&&(l=5),a.splice(l),e.codegenNode=ze(t.helper(vd),a,s)}},jd=(e,t,i,s)=>{let n,{loc:r,modifiers:a,arg:l}=e;if(!e.exp&&a.length,l.type===4)if(l.isStatic){let p=l.content;p.startsWith("vue:")&&(p=`vnode-${p.slice(4)}`),n=oe(t.tagType!==0||p.startsWith("vnode")||!/[A-Z]/.test(p)?Wi(ye(p)):`on:${p}`,!0,l.loc)}else n=At([`${i.helperString(ga)}(`,l,")"]);else(n=l).children.unshift(`${i.helperString(ga)}(`),n.children.push(")");let o=e.exp;o&&!o.content.trim()&&(o=void 0);let c=i.cacheHandlers&&!o&&!i.inVOnce;if(o){let p,f=_d(o),y=!(f||(p=o,Zh.test(kd(p)))),m=o.content.includes(";");(y||c&&f)&&(o=At([`${y?"$event":"(...args)"} => ${m?"{":"("}`,o,m?"}":")"]))}let d={props:[je(n,o||oe("() => {}",!1,r))]};return s&&(d=s(d)),c&&(d.props[0].value=i.cache(d.props[0].value)),d.props.forEach(p=>p.key.isHandlerKey=!0),d},um=(e,t,i)=>{let{modifiers:s}=e,n=e.arg,{exp:r}=e;return r&&r.type===4&&!r.content.trim()&&(r=void 0),n.type!==4?(n.children.unshift("("),n.children.push(') || ""')):n.isStatic||(n.content=n.content?`${n.content} || ""`:'""'),s.some(a=>a.content==="camel")&&(n.type===4?n.isStatic?n.content=ye(n.content):n.content=`${i.helperString(va)}(${n.content})`:(n.children.unshift(`${i.helperString(va)}(`),n.children.push(")"))),!i.inSSR&&(s.some(a=>a.content==="prop")&&ko(n,"."),s.some(a=>a.content==="attr")&&ko(n,"^")),{props:[je(n,r)]}},ko=(e,t)=>{e.type===4?e.isStatic?e.content=t+e.content:e.content=`\`${t}\${${e.content}}\``:(e.children.unshift(`'${t}' + (`),e.children.push(")"))},hm=(e,t)=>{if(e.type===0||e.type===1||e.type===11||e.type===10)return()=>{let i,s=e.children,n=!1;for(let r=0;r<s.length;r++){let a=s[r];if(Kr(a)){n=!0;for(let l=r+1;l<s.length;l++){let o=s[l];if(Kr(o))i||(i=s[r]=At([a],a.loc)),i.children.push(" + ",o),s.splice(l,1),l--;else{i=void 0;break}}}}if(n&&(s.length!==1||e.type!==0&&(e.type!==1||e.tagType!==0||e.props.find(r=>r.type===7&&!t.directiveTransforms[r.name]))))for(let r=0;r<s.length;r++){let a=s[r];if(Kr(a)||a.type===8){let l=[];(a.type!==2||a.content!==" ")&&l.push(a),t.ssr||ft(a,t)!==0||l.push("1"),s[r]={type:12,content:a,loc:a.loc,codegenNode:ze(t.helper(tl),l)}}}}},_o=new WeakSet,mm=(e,t)=>{if(e.type===1&&_t(e,"once",!0)&&!_o.has(e)&&!t.inVOnce&&!t.inSSR)return _o.add(e),t.inVOnce=!0,t.helper(Yn),()=>{t.inVOnce=!1;let i=t.currentNode;i.codegenNode&&(i.codegenNode=t.cache(i.codegenNode,!0,!0))}},Ld=(e,t,i)=>{let s,{exp:n,arg:r}=e;if(!n)return i.onError(be(41,e.loc)),wn();let a=n.loc.source.trim(),l=n.type===4?n.content:a,o=i.bindingMetadata[a];if(o==="props"||o==="props-aliased"||o==="literal-const"||o==="setup-const")return n.loc,wn();if(!l.trim()||!_d(n))return i.onError(be(42,n.loc)),wn();let c=r||oe("modelValue",!0),d=r?pt(r)?`onUpdate:${ye(r.content)}`:At(['"onUpdate:" + ',r]):"onUpdate:modelValue",p=i.isTS?"($event: any)":"$event";s=At([`${p} => ((`,n,") = $event)"]);let f=[je(c,e.exp),je(d,s)];if(e.modifiers.length&&t.tagType===1){let y=e.modifiers.map(x=>x.content).map(x=>(xa.test(x)?JSON.stringify(x):x)+": true").join(", "),m=r?pt(r)?`${r.content}Modifiers`:At([r,' + "Modifiers"']):"modelModifiers";f.push(je(m,oe(`{ ${y} }`,!1,e.loc,2)))}return wn(f)};function wn(e=[]){return{props:e}}var So=new WeakSet,fm=(e,t)=>{if(e.type===1){let i=_t(e,"memo");if(!(!i||So.has(e))&&!t.inSSR)return So.add(e),()=>{let s=e.codegenNode||t.currentNode.codegenNode;s&&s.type===13&&(e.tagType!==1&&pl(s,t),e.codegenNode=ze(t.helper(dl),[i.exp,as(void 0,s),"_cache",String(t.cached.length)]),t.cached.push(null))}}},vm=(e,t)=>{if(e.type===1){for(let i of e.props)if(i.type===7&&i.name==="bind"&&(!i.exp||i.exp.type===4&&!i.exp.content.trim())&&i.arg){let s=i.arg;if(s.type===4&&s.isStatic){let n=ye(s.content);(wd.test(n[0])||n[0]==="-")&&(i.exp=oe(n,!1,s.loc))}else t.onError(be(53,s.loc)),i.exp=oe("",!0,s.loc)}}},Fd=Symbol(""),zd=Symbol(""),Bd=Symbol(""),Dd=Symbol(""),Ma=Symbol(""),$d=Symbol(""),Ud=Symbol(""),Vd=Symbol(""),Hd=Symbol(""),Kd=Symbol("");Object.getOwnPropertySymbols(so={[Fd]:"vModelRadio",[zd]:"vModelCheckbox",[Bd]:"vModelText",[Dd]:"vModelSelect",[Ma]:"vModelDynamic",[$d]:"withModifiers",[Ud]:"withKeys",[Vd]:"vShow",[Hd]:"Transition",[Kd]:"TransitionGroup"}).forEach(e=>{rs[e]=so[e]});var gm={parseMode:"html",isVoidTag:Np,isNativeTag:e=>Mp(e)||Ap(e)||Ip(e),isPreTag:e=>e==="pre",isIgnoreNewlineTag:e=>e==="pre"||e==="textarea",decodeEntities:function(e,t=!1){return Fi||(Fi=document.createElement("div")),t?(Fi.innerHTML=`<div foo="${e.replace(/"/g,"&quot;")}">`,Fi.children[0].getAttribute("foo")):(Fi.innerHTML=e,Fi.textContent)},isBuiltInComponent:e=>e==="Transition"||e==="transition"?Hd:e==="TransitionGroup"||e==="transition-group"?Kd:void 0,getNamespace(e,t,i){let s=t?t.ns:i;if(t&&s===2)if(t.tag==="annotation-xml"){if(e==="svg")return 1;t.props.some(n=>n.type===6&&n.name==="encoding"&&n.value!=null&&(n.value.content==="text/html"||n.value.content==="application/xhtml+xml"))&&(s=0)}else/^m(?:[ions]|text)$/.test(t.tag)&&e!=="mglyph"&&e!=="malignmark"&&(s=0);else t&&s===1&&(t.tag==="foreignObject"||t.tag==="desc"||t.tag==="title")&&(s=0);if(s===0){if(e==="svg")return 1;if(e==="math")return 2}return s}},bm=bt("passive,once,capture"),ym=bt("stop,prevent,self,ctrl,shift,alt,meta,exact,middle"),xm=bt("left,right"),qo=bt("onkeyup,onkeydown,onkeypress"),To=(e,t)=>pt(e)&&e.content.toLowerCase()==="onclick"?oe(t,!0):e.type!==4?At(["(",e,`) === "onClick" ? "${t}" : (`,e,")"]):e,wm=(e,t)=>{e.type===1&&e.tagType===0&&(e.tag==="script"||e.tag==="style")&&t.removeNode()},km=[e=>{e.type===1&&e.props.forEach((t,i)=>{let s,n;t.type===6&&t.name==="style"&&t.value&&(e.props[i]={type:7,name:"bind",arg:oe("style",!0,t.loc),exp:(s=t.value.content,n=t.loc,oe(JSON.stringify(Ao(s)),!1,n,3)),modifiers:[],loc:t.loc})})}],_m={cloak:()=>({props:[]}),html:(e,t,i)=>{let{exp:s,loc:n}=e;return s||i.onError(be(54,n)),t.children.length&&(i.onError(be(55,n)),t.children.length=0),{props:[je(oe("innerHTML",!0,n),s||oe("",!0))]}},text:(e,t,i)=>{let{exp:s,loc:n}=e;return s||i.onError(be(56,n)),t.children.length&&(i.onError(be(57,n)),t.children.length=0),{props:[je(oe("textContent",!0),s?ft(s,i)>0?s:ze(i.helperString(wr),[s],n):oe("",!0))]}},model:(e,t,i)=>{let s=Ld(e,t,i);if(!s.props.length||t.tagType===1)return s;e.arg&&i.onError(be(59,e.arg.loc));let{tag:n}=t,r=i.isCustomElement(n);if(n==="input"||n==="textarea"||n==="select"||r){let a=Bd,l=!1;if(n==="input"||r){let o=kr(t,"type");if(o){if(o.type===7)a=Ma;else if(o.value)switch(o.value.content){case"radio":a=Fd;break;case"checkbox":a=zd;break;case"file":l=!0,i.onError(be(60,e.loc))}}else t.props.some(c=>c.type===7&&c.name==="bind"&&(!c.arg||c.arg.type!==4||!c.arg.isStatic))&&(a=Ma)}else n==="select"&&(a=Dd);l||(s.needRuntime=i.helper(a))}else i.onError(be(58,e.loc));return s.props=s.props.filter(a=>a.key.type!==4||a.key.content!=="modelValue"),s},on:(e,t,i)=>jd(e,t,i,s=>{let{modifiers:n}=e;if(!n.length)return s;let{key:r,value:a}=s.props[0],{keyModifiers:l,nonKeyModifiers:o,eventOptionModifiers:c}=((d,p,f,y)=>{let m=[],x=[],q=[];for(let b=0;b<p.length;b++){let u=p[b].content;bm(u)?q.push(u):xm(u)?pt(d)?qo(d.content.toLowerCase())?m.push(u):x.push(u):(m.push(u),x.push(u)):ym(u)?x.push(u):m.push(u)}return{keyModifiers:m,nonKeyModifiers:x,eventOptionModifiers:q}})(r,n,0,e.loc);if(o.includes("right")&&(r=To(r,"onContextmenu")),o.includes("middle")&&(r=To(r,"onMouseup")),o.length&&(a=ze(i.helper($d),[a,JSON.stringify(o)])),l.length&&(!pt(r)||qo(r.content.toLowerCase()))&&(a=ze(i.helper(Ud),[a,JSON.stringify(l)])),c.length){let d=c.map(Pi).join("");r=pt(r)?oe(`${r.content}${d}`,!0):At(["(",r,`) + "${d}"`])}return{props:[je(r,a)]}}),show:(e,t,i)=>{let{exp:s,loc:n}=e;return s||i.onError(be(62,n)),{props:[],needRuntime:i.helper(Vd)}}},Co=Object.create(null);function Sm(e,t){if(!re(e))if(e.nodeType)e=e.innerHTML;else return He;let i=e+JSON.stringify(t,(l,o)=>typeof o=="function"?o.toString():o),s=Co[i];if(s)return s;if(e[0]==="#"){let l=document.querySelector(e);e=l?l.innerHTML:""}let n=de({hoistStatic:!0,onError:void 0,onWarn:He},t);!n.isCustomElement&&"u">typeof customElements&&(n.isCustomElement=l=>!!customElements.get(l));let{code:r}=function(l,o={}){return function(c,d={}){var p;let f,y=d.onError||ya,m=d.mode==="module";d.prefixIdentifiers===!0?y(be(48)):m&&y(be(49)),d.cacheHandlers&&y(be(50)),d.scopeId&&!m&&y(be(51));let x=de({},d,{prefixIdentifiers:!1}),q=re(c)?function(h,g){if(Oe.reset(),Ge=null,ve=null,ht="",Ft=-1,xi=-1,qe.length=0,Wt=h,we=de({},Td),g){let S;for(S in g)g[S]!=null&&(we[S]=g[S])}Oe.mode=we.parseMode==="html"?1:2*(we.parseMode==="sfc"),Oe.inXML=we.ns===1||we.ns===2;let _=g&&g.delimiters;_&&(Oe.delimiterOpen=Xn(_[0]),Oe.delimiterClose=Xn(_[1]));let k=ir=function(S,C=""){return{type:0,source:C,children:S,helpers:new Set,components:[],directives:[],hoists:[],imports:[],cached:[],temps:0,codegenNode:void 0,loc:gt}}([],h);return Oe.parse(Wt),k.loc=Ee(0,h.length),k.children=Md(k.children),ir=null,k}(c,x):c,[b,u]=[[vm,mm,lm,fm,om,pm,dm,cm,hm],{on:jd,bind:um,model:Ld}];return f=function(h,{filename:g="",prefixIdentifiers:_=!1,hoistStatic:k=!1,hmr:S=!1,cacheHandlers:C=!1,nodeTransforms:E=[],directiveTransforms:O={},transformHoist:B=null,isBuiltInComponent:T=He,isCustomElement:F=He,expressionPlugins:L=[],scopeId:M=null,slotted:Q=!0,ssr:V=!1,inSSR:J=!1,ssrCssVars:K="",bindingMetadata:te=pe,inline:ne=!1,isTS:he=!1,onError:Ae=ya,onWarn:_e=yd,compatConfig:Ve}){let et=g.replace(/\?.*$/,"").match(/([^/\\]+)\.\w+$/),ce={filename:g,selfName:et&&Pi(ye(et[1])),prefixIdentifiers:_,hoistStatic:k,hmr:S,cacheHandlers:C,nodeTransforms:E,directiveTransforms:O,transformHoist:B,isBuiltInComponent:T,isCustomElement:F,expressionPlugins:L,scopeId:M,slotted:Q,ssr:V,inSSR:J,ssrCssVars:K,bindingMetadata:te,inline:ne,isTS:he,onError:Ae,onWarn:_e,compatConfig:Ve,root:h,helpers:new Map,components:new Set,directives:new Set,hoists:[],imports:[],cached:[],constantCache:new WeakMap,vForMemoKeyedNodes:new WeakSet,temps:0,identifiers:Object.create(null),scopes:{vFor:0,vSlot:0,vPre:0,vOnce:0},parent:null,grandParent:null,currentNode:h,childIndex:0,inVOnce:!1,helper(ae){let xe=ce.helpers.get(ae)||0;return ce.helpers.set(ae,xe+1),ae},removeHelper(ae){let xe=ce.helpers.get(ae);if(xe){let Se=xe-1;Se?ce.helpers.set(ae,Se):ce.helpers.delete(ae)}},helperString:ae=>`_${rs[ce.helper(ae)]}`,replaceNode(ae){ce.parent.children[ce.childIndex]=ce.currentNode=ae},removeNode(ae){let xe=ce.parent.children,Se=ae?xe.indexOf(ae):ce.currentNode?ce.childIndex:-1;ae&&ae!==ce.currentNode?ce.childIndex>Se&&(ce.childIndex--,ce.onNodeRemoved()):(ce.currentNode=null,ce.onNodeRemoved()),ce.parent.children.splice(Se,1)},onNodeRemoved:He,addIdentifiers(ae){},removeIdentifiers(ae){},hoist(ae){re(ae)&&(ae=oe(ae)),ce.hoists.push(ae);let xe=oe(`_hoisted_${ce.hoists.length}`,!1,ae.loc,2);return xe.hoisted=ae,xe},cache(ae,xe=!1,Se=!1){let v=function(w,A,$=!1,P=!1){return{type:20,index:w,value:A,needPauseTracking:$,inVOnce:P,needArraySpread:!1,loc:gt}}(ce.cached.length,ae,xe,Se);return ce.cached.push(v),v}};return ce}(q,p=de({},x,{nodeTransforms:[...b,...d.nodeTransforms||[]],directiveTransforms:de({},u,d.directiveTransforms||{})})),sr(q,f),p.hoistStatic&&function h(g,_,k,S=!1,C=!1){let{children:E}=g,O=[];for(let L=0;L<E.length;L++){let M=E[L];if(M.type===1&&M.tagType===0){let Q=S?0:ft(M,k);if(Q>0){if(Q>=2){M.codegenNode.patchFlag=-1,O.push(M);continue}}else{let V=M.codegenNode;if(V.type===13){let J=V.patchFlag;if((J===void 0||J===512||J===1)&&Id(M,k)>=2){let K=Nd(M);K&&(V.props=k.hoist(K))}V.dynamicProps&&(V.dynamicProps=k.hoist(V.dynamicProps))}}}else if(M.type===12&&(S?0:ft(M,k))>=2){M.codegenNode.type===14&&M.codegenNode.arguments.length>0&&M.codegenNode.arguments.push("-1"),O.push(M);continue}if(M.type===1){let Q=M.tagType===1;Q&&k.scopes.vSlot++,h(M,g,k,!1,C),Q&&k.scopes.vSlot--}else if(M.type===11)h(M,g,k,M.children.length===1,!0);else if(M.type===9)for(let Q=0;Q<M.branches.length;Q++)h(M.branches[Q],g,k,M.branches[Q].children.length===1,C)}let B=!1;if(O.length===E.length&&g.type===1){if(g.tagType===0&&g.codegenNode&&g.codegenNode.type===13&&G(g.codegenNode.children))g.codegenNode.children=T(Ci(g.codegenNode.children)),B=!0;else if(g.tagType===1&&g.codegenNode&&g.codegenNode.type===13&&g.codegenNode.children&&!G(g.codegenNode.children)&&g.codegenNode.children.type===15){let L=F(g.codegenNode,"default");L&&(L.returns=T(Ci(L.returns)),B=!0)}else if(g.tagType===3&&_&&_.type===1&&_.tagType===1&&_.codegenNode&&_.codegenNode.type===13&&_.codegenNode.children&&!G(_.codegenNode.children)&&_.codegenNode.children.type===15){let L=_t(g,"slot",!0),M=L&&L.arg&&F(_.codegenNode,L.arg);M&&(M.returns=T(Ci(M.returns)),B=!0)}}if(!B)for(let L of O)L.codegenNode=k.cache(L.codegenNode);function T(L){let M=k.cache(L);return M.needArraySpread=!0,M}function F(L,M){if(L.children&&!G(L.children)&&L.children.type===15){let Q=L.children.properties.find(V=>V.key===M||V.key.content===M);return Q&&Q.value}}O.length&&k.transformHoist&&k.transformHoist(E,k,g)}(q,void 0,f,!!uo(q)),p.ssr||function(h,g){let{helper:_}=g,{children:k}=h;if(k.length===1){let S=uo(h);if(S&&S.codegenNode){let C=S.codegenNode;C.type===13&&pl(C,g),h.codegenNode=C}else h.codegenNode=k[0]}else k.length>1&&(h.codegenNode=Us(g,_(Ds),void 0,h.children,64,void 0,void 0,!0,void 0,!1))}(q,f),q.helpers=new Set([...f.helpers.keys()]),q.components=[...f.components],q.directives=[...f.directives],q.imports=f.imports,q.hoists=f.hoists,q.temps=f.temps,q.cached=f.cached,q.transformed=!0,function(h,g={}){let _=function(V,{mode:J="function",prefixIdentifiers:K=J==="module",sourceMap:te=!1,filename:ne="template.vue.html",scopeId:he=null,optimizeImports:Ae=!1,runtimeGlobalName:_e="Vue",runtimeModuleName:Ve="vue",ssrRuntimeModuleName:et="vue/server-renderer",ssr:ce=!1,isTS:ae=!1,inSSR:xe=!1}){let Se={mode:J,prefixIdentifiers:K,sourceMap:te,filename:ne,scopeId:he,optimizeImports:Ae,runtimeGlobalName:_e,runtimeModuleName:Ve,ssrRuntimeModuleName:et,ssr:ce,isTS:ae,inSSR:xe,source:V.source,code:"",column:1,line:1,offset:0,indentLevel:0,pure:!1,map:void 0,helper:w=>`_${rs[w]}`,push(w,A=-2,$){Se.code+=w},indent(){v(++Se.indentLevel)},deindent(w=!1){w?--Se.indentLevel:v(--Se.indentLevel)},newline(){v(Se.indentLevel)}};function v(w){Se.push(`
`+"  ".repeat(w),0)}return Se}(h,g);g.onContextCreated&&g.onContextCreated(_);let{mode:k,push:S,prefixIdentifiers:C,indent:E,deindent:O,newline:B,ssr:T}=_,F=Array.from(h.helpers),L=F.length>0,M=!C&&k!=="module";(function(V,J){let{push:K,newline:te,runtimeGlobalName:ne}=J,he=Array.from(V.helpers);if(he.length>0&&(K(`const _Vue = ${ne}
`,-1),V.hoists.length)){let Ae=[di,pi,Zs,tl,fd].filter(_e=>he.includes(_e)).map(ho).join(", ");K(`const { ${Ae} } = _Vue
`,-1)}(function(Ae,_e){if(!Ae.length)return;_e.pure=!0;let{push:Ve,newline:et}=_e;et();for(let ce=0;ce<Ae.length;ce++){let ae=Ae[ce];ae&&(Ve(`const _hoisted_${ce+1} = `),st(ae,_e),et())}_e.pure=!1})(V.hoists,J),te(),K("return ")})(h,_);let Q=(T?["_ctx","_push","_parent","_attrs"]:["_ctx","_cache"]).join(", ");if(S(`function ${T?"ssrRender":"render"}(${Q}) {`),E(),M&&(S("with (_ctx) {"),E(),L&&(S(`const { ${F.map(ho).join(", ")} } = _Vue
`,-1),B())),h.components.length&&(mo(h.components,"component",_),(h.directives.length||h.temps>0)&&B()),h.directives.length&&(mo(h.directives,"directive",_),h.temps>0&&B()),h.temps>0){S("let ");for(let V=0;V<h.temps;V++)S(`${V>0?", ":""}_temp${V}`)}return(h.components.length||h.directives.length||h.temps)&&(S(`
`,0),B()),T||S("return "),h.codegenNode?st(h.codegenNode,_):S("null"),M&&(O(),S("}")),O(),S("}"),{ast:h,code:_.code,preamble:"",map:_.map?_.map.toJSON():void 0}}(q,x)}(l,de({},gm,o,{nodeTransforms:[wm,...km,...o.nodeTransforms||[]],directiveTransforms:de({},_m,o.directiveTransforms||{}),transformHoist:null}))}(e,n),a=Function("Vue",r)(Vh);return a._rc=!0,Co[i]=a}Fc(Sm);var _r=null;function Qd(e){_r=e}async function qm(e,t){if(!_r||!_r.invoke)throw new Error("\u63D2\u4EF6\u8FD0\u884C\u65F6\u672A\u5C31\u7EEA");return await _r.invoke(e,t||{})}async function at(e,t){let i=await qm(e,t);return i&&typeof i=="object"&&"data"in i&&i.data!==null&&i.data!==void 0?i.data:i}var W=ui({ready:!1,err:"",uin:"",sessions:[],sid:"",msgs:[],loading:!1,loadingMore:!1,hasMore:!0,keyword:"",msgKeyword:"",viewer:"",pageSize:50,cap:600,atBottom:!0});async function Wd(){try{let e=await at("qqbot.account.info");W.uin=String(e&&(e.uin||e.self_id)||"")}catch{}}async function cs(e){W.err="";try{let t=await at("qqbot.chat.sessions",{limit:200,kw:e||""}),i=t&&t.items||[];W.sessions=i.filter(s=>s&&s.target_id),!W.sid&&W.sessions.length&&(W.sid=W.sessions[0].session_id),W.ready=!0}catch(t){W.err=String(t&&t.message||t)}}async function ds(e,t){e&&(W.sid=e,W.msgKeyword=String(t||""),W.msgs=[],W.hasMore=!0,W.atBottom=!0,await tn(!1))}async function tn(e){if(W.sid&&!(e&&(W.loadingMore||!W.hasMore))){e?W.loadingMore=!0:W.loading=!0;try{let t={session_id:W.sid,limit:W.pageSize};W.msgKeyword&&(t.kw=W.msgKeyword),e&&W.msgs.length&&(t.before_id=W.msgs[0].id);let i=await at("qqbot.chat.messages",t),s=i&&i.items||[];e?(W.msgs=s.concat(W.msgs),W.msgs.length>W.cap&&(W.msgs=W.msgs.slice(-W.cap))):W.msgs=s,W.hasMore=s.length>=W.pageSize}catch(t){W.err=String(t&&t.message||t)}finally{W.loading=!1,W.loadingMore=!1}}}function Jd(){return W.sessions.find(e=>e.session_id===W.sid)||null}function Gd(e){if(!e)return!1;if(e.role==="assistant")return!0;let t=String(e.sender_id||"");return!!(W.uin&&t&&t===W.uin)}var Yd="rcq.im.read";function Xd(){try{return JSON.parse(localStorage.getItem(Yd)||"{}")||{}}catch{return{}}}function Sr(e){let t=W.sessions.find(i=>i.session_id===e);return t&&Number(t.last_read_id||0)>0?Number(t.last_read_id):Number(Xd()[e]||0)}function Zd(e,t){if(!e||!t)return;let i=Xd();if(!(Number(i[e]||0)>=Number(t))){i[e]=Number(t);try{localStorage.setItem(Yd,JSON.stringify(i))}catch{}try{let s=at("qqbot.chat.session_ui",{session_id:e,last_read_id:Number(t)});s&&s.catch&&s.catch(()=>{})}catch{}}}var ep=e=>e<10?"0"+e:""+e;function Tr(e){if(!e)return"";let t=new Date(e*1e3);return ep(t.getHours())+":"+ep(t.getMinutes())}function qr(e){let t=new Date(e);return t.setHours(0,0,0,0),t.getTime()}function tp(e){if(!e)return"";let t=new Date(e*1e3),i=qr(Date.now()),s=qr(t),n=Math.round((i-s)/864e5);return n===0?Tr(e):n===1?"\u6628\u5929":t.getFullYear()===new Date().getFullYear()?t.getMonth()+1+"\u6708"+t.getDate()+"\u65E5":t.getFullYear()+"/"+(t.getMonth()+1)+"/"+t.getDate()}function ip(e){if(!e)return"";let t=new Date(e*1e3),i=Math.round((qr(Date.now())-qr(t))/864e5),s=Tr(e);return i===0?s:i===1?"\u6628\u5929 "+s:(t.getFullYear()===new Date().getFullYear()?t.getMonth()+1+"\u6708"+t.getDate()+"\u65E5 ":t.getFullYear()+"\u5E74"+(t.getMonth()+1)+"\u6708"+t.getDate()+"\u65E5 ")+s}function ps(e){if(!e)return"";if(e._url)return e._url;let t=e.abs||(e.rel?"/opt/rcbot/media/"+e.rel:"");return t?"/api/fm/preview?path="+encodeURIComponent(t):""}function us(e){return!e||!e.local?!1:e.exists!==0}function Cr(e){let t=String(e===0?0:e||"").trim();return/^\d+$/.test(t)?"https://qzonestyle.gtimg.cn/qzone/em/e"+t+".gif":""}function Mr(e){return e=Number(e)||0,e>=1073741824?(e/1073741824).toFixed(2)+" GB":e>=1048576?(e/1048576).toFixed(1)+" MB":e>=1024?(e/1024).toFixed(0)+" KB":e+" B"}function sp(e){return e=Number(e)||0,e>=1e8?(e/1e8).toFixed(1)+"\u4EBF":e>=1e4?(e/1e4).toFixed(1)+"\u4E07":String(e)}function sn(e){let t=Array.isArray(e&&e.segs)?e.segs:[],i=[],s="",n=!1;for(let a of t){let l=a&&a.type,o=a&&a.data||{};if(l){if(l==="reply"){s=o.text||"[\u5F15\u7528\u4E86\u4E00\u6761\u6D88\u606F]";continue}switch(l){case"text":o.text&&i.push({t:"text",v:o.text});break;case"at":i.push({t:"at",v:o.qq==="all"?"@\u5168\u4F53\u6210\u5458":"@"+(o.name||o.qq||"\u67D0\u4EBA")});break;case"face":i.push({t:"face",v:o.id});break;case"markdown":i.push({t:"text",v:o.content||"[Markdown \u6D88\u606F]"});break;case"image":case"video":case"record":case"file":case"mface":case"json":case"xml":case"forward":case"node":case"location":case"contact":case"music":case"rps":case"dice":case"shake":case"poke":break;default:i.push({t:"unknown",name:l});break}}}let r=Array.isArray(e&&e.media)?e.media:[];return!i.length&&!r.length&&e&&e.text&&i.push({t:"text",v:e.text}),e&&e.role==="system"&&(n=!0),{quote:s,parts:i,system:n}}function np(e){let t={image:[],video:[],record:[],file:[],face:[],other:[]};for(let i of e||[]){if(!i||!i.local)continue;let s=i.kind==="mface"?"face":i.kind;(t[s]||t.other).push(i)}return t}function Ar(e){return e<=1?"g1":e===2||e===4?"g2":"g3"}function rp(e){let t=Math.max(1,Math.min(60,Number(e)||1));return Math.round(96+t*3.2)}function ap(e){let t=Number(e&&e.bytes||0);return t?Math.max(1,Math.min(60,Math.round(t/3e3))):2}function nn(e){let t=Array.isArray(e&&e.segs)?e.segs:[];for(let i of t)if(i&&i.type==="forward"){let s=(i.data||{}).id;if(s)return String(s)}return""}var hi=null;function Tm(e){for(let t of e||[]){let i=t&&t.type,s=t&&t.data||{};if(i==="json")try{let n=JSON.parse(s.data),r=n.meta||{},a=n.prompt||r.detail&&r.detail.title||r.news&&r.news.title||"\u5361\u7247\u6D88\u606F",l=r.detail&&r.detail.desc||r.desc||"",o=r.news&&r.news.jumpUrl||r.detail&&r.detail.qqdocurl||"";return{kind:"card",title:a,desc:l,jump:o}}catch{return{kind:"card",title:"\u5361\u7247\u6D88\u606F",desc:"",jump:""}}if(i==="xml")return{kind:"card",title:"\u5361\u7247\u6D88\u606F",desc:String(s.data||"").slice(0,90),jump:""};if(i==="forward"||i==="node")return{kind:"forward",title:"\u5408\u5E76\u8F6C\u53D1",desc:"\u70B9\u51FB\u67E5\u770B\u5185\u5BB9",jump:""}}return null}var Cm={props:{m:Object,me:Boolean},data(){return{playing:!1}},computed:{sec(){return ap(this.m)},w(){return rp(this.sec)},src(){return ps(this.m)},bars(){let e=this.sec,t=Math.max(6,Math.min(22,Math.round(e*1.6))),i=[];for(let s=0;s<t;s++)i.push(6+Math.round(Math.abs(Math.sin(s*1.7+e))*12));return i}},beforeUnmount(){this.stop()},methods:{stop(){if(hi)try{hi.pause()}catch{}this.playing=!1},toggle(){if(this.src){if(this.playing){this.stop();return}if(hi)try{hi.pause()}catch{}hi=new Audio(this.src),hi.onended=()=>{this.playing=!1},hi.onerror=()=>{this.playing=!1},hi.play().then(()=>{this.playing=!0}).catch(()=>{this.playing=!1})}}},template:`
  <div class="im-voice" :style="{ width: w + 'px' }" @click="toggle" :title="playing ? '\u505C\u6B62' : '\u64AD\u653E\u8BED\u97F3'">
    <span class="wave">
      <i v-for="(h,i) in bars" :key="i" :style="{ height: h + 'px', opacity: playing ? .95 : .5 }"></i>
    </span>
    <span class="sec">{{ sec }}"</span>
  </div>`},lp={components:{ImVoice:Cm},props:{m:Object,compact:Boolean,showTime:String},data(){return{viewer:"",badAva:!1}},computed:{me(){return Gd(this.m)},recalled(){return!!this.m.recalled},parsed(){return sn(this.m)},parts(){return this.parsed.parts},quote(){let e=this.m&&this.m.quote;return e&&(e.sender||e.text)?(e.sender?e.sender+"\uFF1A":"")+(e.text||"[\u6D88\u606F]"):this.parsed.quote},media(){return this.m.media||[]},groups(){return np(this.media)},card(){let e=Tm(this.m.segs);return e&&e.kind==="forward"&&this.m._fwdCount&&(e.desc=this.m._fwdCount+" \u6761\u6D88\u606F"),e},forwardId(){return nn(this.m)},hasMedia(){return!!(this.groups.image.length||this.groups.video.length||this.groups.record.length||this.groups.file.length)},mediaOnly(){return!this.quote&&!this.parts.filter(e=>e.t!=="face").length&&this.hasMedia},name(){return this.m.sender_name||this.m.sender_id||"\u672A\u77E5"},avatar(){if(this.m.sender_avatar)return this.m.sender_avatar;let e=String(this.m.sender_id||"");return/^\d{5,12}$/.test(e)?"https://q1.qlogo.cn/g?b=qq&nk="+e+"&s=100":""},time(){return Tr(this.m.created_at)},recalledBy(){let e=String(this.m&&this.m.recalled_by||"");if(!e)return"";let t=W.msgs.find(i=>String(i.sender_id||"")===e);return t&&t.sender_name||""},recalledTip(){let e=this.recalledBy;return e?"\u7531 "+e+" \u64A4\u56DE":"\u6D88\u606F\u5DF2\u88AB\u64A4\u56DE"},initial(){return String(this.name||"?").trim().slice(0,1)},showAva(){return!!this.avatar&&!this.badAva},canRecall(){return this.me&&!!this.m.msg_id},images(){return this.groups.image.filter(us)},videos(){return this.groups.video.filter(us)},voices(){return this.groups.record.filter(us)},files(){return this.groups.file.filter(us)}},methods:{faceUrl:Cr,mediaUrl:ps,bytes:Mr,gridCls:Ar,mediaAlive:us,openImg(e){this.viewer=ps(e)},faceErr(e){let t=e&&e.target;t&&(t.style.visibility="hidden")}},template:`
  <div>
    <div class="im-time" v-if="showTime">{{ showTime }}</div>
    <div class="im-msg" :class="{ me: me, compact: compact, recalled: recalled }" :data-mid="m.id"
      :data-msgid="m.msg_id || ''"
      @contextmenu.prevent="$emit('ctx', $event, m)">
      <div class="ava" :class="{ ph: compact }">
        <img v-if="showAva && !compact" :src="avatar" alt="" @error="badAva = true" />
        <div v-else-if="!compact" class="ava-t">{{ initial }}</div>
      </div>
      <div class="col">
        <div class="who" v-if="!compact && !me">{{ name }}</div>

        <!-- \u2605 \u64A4\u56DE\u7684\u6D88\u606F\u7167\u5E38\u663E\u793A\u5185\u5BB9\uFF08\u8FD9\u662F"\u5168\u91CF\u6863\u6848"\uFF0C\u539F\u6587\u6C38\u4E45\u4FDD\u7559\uFF09\uFF0C
             \u53EA\u5728\u4E0B\u9762\u6253\u4E00\u4E2A\u300C\u5DF2\u64A4\u56DE\u300D\u6807\u8BB0 \u2014\u2014 \u548C\u300C\u804A\u5929\u8BB0\u5F55\u300D\u9875\u7684\u884C\u4E3A\u4FDD\u6301\u4E00\u81F4\u3002 -->
        <div class="im-bub" :class="{ media: mediaOnly }">
          <div class="im-quote" v-if="quote" :title="quote"
            @click.stop="$emit('jump', m.quote && m.quote.msg_id)">{{ quote }}</div>

          <div v-if="card" class="im-card" :class="{ fwd: card.kind === 'forward' }"
            @click.stop="card.kind === 'forward' && forwardId && $emit('forward', forwardId)">
            <div class="ct">{{ card.title }}</div>
            <div class="cd" v-if="card.desc">{{ card.desc }}</div>
          </div>

          <span v-for="(p,i) in parts" :key="i">
            <span v-if="p.t === 'text'">{{ p.v }}</span>
            <span v-else-if="p.t === 'at'" class="at">{{ p.v }}</span>
            <img v-else-if="p.t === 'face'" class="face" :src="faceUrl(p.v)" alt="[\u8868\u60C5]" @error="faceErr" />
            <span v-else class="im-unk">[{{ p.name }}]</span>
          </span>
        </div>

        <!-- \u5A92\u4F53\u533A\uFF08\u653E\u5728\u6C14\u6CE1\u5916\uFF0C\u907F\u514D\u5706\u89D2\u4E0E\u5185\u8FB9\u8DDD\u6253\u67B6\uFF09 -->
        <div class="im-grid" :class="gridCls(images.length)" v-if="images.length">
          <img v-for="(m,i) in images" :key="i" :src="mediaUrl(m)" loading="lazy"
            @click="openImg(m)" alt="\u56FE\u7247" />
        </div>
        <div class="im-video" v-for="(m,i) in videos" :key="'v'+i">
          <video :src="mediaUrl(m)" controls preload="metadata" playsinline></video>
        </div>
        <div class="im-bub" v-for="(m,i) in voices" :key="'r'+i" style="padding:6px 10px">
          <im-voice :m="m" :me="me" />
        </div>
        <div class="im-bub" v-for="(m,i) in files" :key="'f'+i" style="padding:8px 12px">
          <div class="im-file">
            <div class="fi">{{ (m.name || 'FILE').split('.').pop().slice(0,4).toUpperCase() }}</div>
            <div style="min-width:0">
              <div style="font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
                {{ m.name || '\u6587\u4EF6' }}</div>
              <div style="font-size:11px;color:var(--im-t3)">{{ bytes(m.bytes) }}</div>
            </div>
            <a :href="mediaUrl(m)" :download="m.name || true" style="margin-left:8px;font-size:12px">\u4E0B\u8F7D</a>
          </div>
        </div>

        <div class="im-ops">
          <button class="im-op" title="\u590D\u5236\u6587\u5B57" @click.stop="$emit('copy', m)">\u590D\u5236</button>
          <button class="im-op" v-if="canRecall" title="\u64A4\u56DE" @click.stop="$emit('recall', m)">\u64A4\u56DE</button>
        </div>

        <div class="im-meta" v-if="!compact">
          <span>{{ time }}</span>
          <span class="im-rec-tag" v-if="recalled" :title="recalledTip">\u5DF2\u64A4\u56DE</span>
        </div>
      </div>
    </div>

    <div class="im-viewer" v-if="viewer" @click.self="viewer = ''">
      <button class="x" @click="viewer = ''">\xD7</button>
      <img :src="viewer" alt="" />
    </div>
  </div>`};var Mm=[{id:"im",title:"\u6D88\u606F",d:"M4 5.5A2.5 2.5 0 016.5 3h11A2.5 2.5 0 0120 5.5v8a2.5 2.5 0 01-2.5 2.5H9l-4 4V16H6.5A2.5 2.5 0 014 13.5v-8z"},{id:"contacts",title:"\u8054\u7CFB\u4EBA",d:"M12 12a4 4 0 100-8 4 4 0 000 8zm-8 8a8 8 0 0116 0v1H4v-1z"},{id:"star",title:"\u6536\u85CF",d:"M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1L3.2 9.5l6.1-.9L12 3z"}],op={components:{ImMessageRow:lp},props:{},data(){return{S:W,rail:"im",railItems:Mm,showJump:!1,dragging:!1,sideWidth:268,badAva:{},menu:null,readAt:0,toastMsg:"",fwd:null,fwdStack:[],sessMenu:null,searchOpen:!1,msgKw:"",rnd:null,rpCfg:{enabled:!0,scope:"enabled_groups"},busy:""}},computed:{cur(){return Jd()},filtered(){let e=(W.keyword||"").trim().toLowerCase();return e?W.sessions.filter(t=>(t.display||"").toLowerCase().includes(e)||String(t.target_id||"").includes(e)):W.sessions},rows(){let e=[],t=0,i="",s=!1;for(let n of W.msgs){if(!n)continue;let r=String(n.text||""),a=n.role==="system"||!(n.segs||[]).length&&r.indexOf("\u64A4\u56DE")>=0,l=n.created_at-t,o=!t||l>300?ip(n.created_at):"";if(a){let f=(r||"\u6709\u4EBA\u64A4\u56DE\u4E86\u4E00\u6761\u6D88\u606F").replace(/^\[/,"").replace(/\]$/,"");e.push({type:"sys",key:"s"+n.id,text:f}),t=n.created_at,i="";continue}let c=String(n.sender_id||n.role||""),d=!o&&c===i&&l<300,p={type:"msg",key:n.id,m:n,compact:d,showTime:o};!s&&this.readAt&&Number(n.id)>this.readAt&&(p.divider=!0,s=!0),e.push(p),t=n.created_at,i=c}return e},total(){return this.cur&&this.cur.msg_count||W.msgs.length}},async mounted(){await Wd(),await cs();try{let t=((await at("rcbot.config.get")||{}).features||{}).random_pick||{};this.rpCfg={enabled:t.enabled!==!1,scope:t.scope||"enabled_groups"}}catch{}W.sid&&(await ds(W.sid),this.readAt=Sr(W.sid),this.scheduleRead()),this.$nextTick(()=>this.toBottom(!1)),window.addEventListener("keydown",this.onKey),window.addEventListener("click",this.closeMenu),document.documentElement.style.overflow="hidden"},beforeUnmount(){window.removeEventListener("keydown",this.onKey),window.removeEventListener("click",this.closeMenu),document.documentElement.style.overflow=""},methods:{fmtListTime:tp,fmtNum:sp,partsOf:sn,gridCls:Ar,mediaUrl:ps,faceUrl:Cr,bytes:Mr,forwardIdOf:nn,onKey(e){e.key==="Escape"&&(e.stopPropagation(),this.close())},close(){this.$emit("close")},closeMenu(){this.menu=null,this.sessMenu=null},onKwInput(){clearTimeout(this._kwTimer),this._kwTimer=setTimeout(()=>{cs(W.keyword)},350)},toggleSearch(){this.searchOpen=!this.searchOpen,!this.searchOpen&&this.msgKw&&this.onSearch(""),this.$nextTick(()=>{let e=this.$refs.msgSearch;e&&this.searchOpen&&e.focus()})},onSearch(e){let t=String(e||"").trim();this.msgKw=t,t!==W.msgKeyword&&ds(W.sid,t).then(()=>{this.$nextTick(()=>this.toBottom(!1)),this.schedulePendingRefresh()})},openRandom(){if(!this.rpCfg.enabled){this.toast("\u968F\u673A\u6311\u6D88\u606F\u56DE\u5DF2\u5173\u95ED\uFF08\u8BBE\u7F6E \u2192 \u80FD\u529B\uFF09");return}this.rnd={loading:!1,scope:this.rpCfg.scope,picked:null,reply:"",provider:"",error:""},this.pickRandom()},closeRandom(){this.rnd=null},async pickRandom(){if(this.rnd){this.rnd.loading=!0,this.rnd.error="";try{let e=await at("qqbot.chat.random_reply",{sid:W.sid||"",scope:this.rnd.scope});this.rnd.picked=e&&e.picked||null,this.rnd.reply=e&&e.reply||"",this.rnd.provider=e&&e.provider||"",this.rnd.token=e&&e.token||"",this.rnd.sent=""}catch(e){this.rnd.error=String(e&&e.message||e),this.rnd.picked=null,this.rnd.reply="",this.rnd.token="",this.rnd.sent=""}finally{this.rnd.loading=!1}}},async sendRandom(){if(!this.rnd||!this.rnd.token)return;let e=this.rnd.picked||{},t=e.title||e.target_id||"";if(confirm("\u628A\u8FD9\u6761\u56DE\u590D\u53D1\u5230\u300C"+t+`\u300D\uFF1F

\u4F1A @ \u4E00\u4E0B\u539F\u8BF4\u8BDD\u4EBA\u3002`)){this.rnd.sending=!0,this.rnd.sent="";try{let i=await at("qqbot.chat.random_reply.send",{token:this.rnd.token});this.rnd.token="",this.rnd.sent="\u5DF2\u53D1\u5230\u300C"+t+"\u300D",this.toast("\u5DF2\u53D1\u9001\u5230 QQ"),tn(!1)}catch(i){this.rnd.sent="\u53D1\u9001\u5931\u8D25\uFF1A"+String(i&&i.message||i)}finally{this.rnd.sending=!1}}},switchScope(){this.rnd&&(this.rnd.scope=this.rnd.scope==="session"?this.rpCfg.scope:"session",this.pickRandom())},scopeLabel(e){return e==="session"?"\u5F53\u524D\u4F1A\u8BDD":e==="all_groups"?"\u6240\u6709\u7FA4\u804A":"\u5DF2\u542F\u7528\u7684\u7FA4\u804A"},async exportSession(e){let t=e&&e.session_id||W.sid;if(this.sessMenu=null,!!t){this.busy="exp";try{let i=await at("qqbot.chat.export",{session_id:t}),s=new Blob([JSON.stringify(i,null,2)],{type:"application/json"}),n=document.createElement("a");n.href=URL.createObjectURL(s),n.download="chat-"+String(t).replace(/[^\w-]/g,"_")+"-"+Date.now()+".json",n.click(),setTimeout(()=>URL.revokeObjectURL(n.href),3e3),this.toast("\u5DF2\u5BFC\u51FA\u4F1A\u8BDD\u8BB0\u5F55")}catch(i){this.toast(String(i&&i.message||i))}finally{this.busy=""}}},async clearSession(e){let t=e&&e.session_id||W.sid,i=e?e.display||e.target_id:"\u8FD9\u4E2A\u4F1A\u8BDD";if(this.sessMenu=null,!t||!confirm("\u6E05\u7A7A\u4F1A\u8BDD\u300C"+i+`\u300D\u7684\u5168\u90E8\u804A\u5929\u8BB0\u5F55\uFF1F

\u6B64\u64CD\u4F5C\u4E0D\u53EF\u64A4\u9500\u3002`))return;let s=confirm(`\u8981\u8FDE\u56FE\u7247/\u89C6\u9891/\u8BED\u97F3\u8FD9\u4E9B\u5A92\u4F53\u6587\u4EF6\u4E00\u8D77\u5220\u6389\u5417\uFF1F

\u786E\u5B9A = \u4E00\u8D77\u5220
\u53D6\u6D88 = \u53EA\u5220\u6587\u5B57\u8BB0\u5F55\uFF08\u5A92\u4F53\u4FDD\u7559\uFF09`);this.busy="clear";try{let n=await at("qqbot.chat.clear_session",{session_id:t,with_media:s,confirm:!0});this.toast("\u5DF2\u6E05\u7A7A "+(n&&n.messages||0)+" \u6761\u6D88\u606F"),await cs(),await ds(W.sid,W.msgKeyword)}catch(n){this.toast(String(n&&n.message||n))}finally{this.busy=""}},hasPending(){for(let e of W.msgs)for(let t of e.media||[])if(t&&t.transcode==="pending")return!0;return!1},schedulePendingRefresh(){clearTimeout(this._pendTimer),this.hasPending()&&(this._pendTimer=setTimeout(async()=>{this._pendTimer=null,await tn(!1),this.schedulePendingRefresh()},6e3))},openSessMenu(e,t){this.sessMenu={x:e.clientX,y:e.clientY,s:t}},async togglePin(e){if(this.sessMenu=null,!!e)try{let t=await at("qqbot.chat.session_ui",{session_id:e.session_id,pinned:!e.pinned});e.pinned=t&&typeof t.pinned<"u"?t.pinned:e.pinned?0:1,this.toast(e.pinned?"\u5DF2\u7F6E\u9876":"\u5DF2\u53D6\u6D88\u7F6E\u9876"),await cs()}catch(t){this.toast(String(t&&t.message||t))}},async toggleMute(e){if(this.sessMenu=null,!!e)try{let t=await at("qqbot.chat.session_ui",{session_id:e.session_id,muted:!e.muted});e.muted=t&&typeof t.muted<"u"?t.muted:e.muted?0:1,this.toast(e.muted?"\u5DF2\u514D\u6253\u6270":"\u5DF2\u53D6\u6D88\u514D\u6253\u6270")}catch(t){this.toast(String(t&&t.message||t))}},markReadNow(e){if(this.sessMenu=null,!e)return;let t=Sr(e.session_id);t&&at("qqbot.chat.session_ui",{session_id:e.session_id,last_read_id:t}).catch(()=>{}),e.unread=0},async openForward(e){if(e){this.fwd&&this.fwdStack.push(this.fwd),this.fwd={id:e,loading:!0,nodes:[],total:0,error:""};try{let t=await at("qqbot.chat.forward",{id:e}),i=t&&t.total||0;this.fwd={id:e,loading:!1,nodes:t&&t.nodes||[],total:i,error:""};for(let s of W.msgs)if(nn(s)===e){s._fwdCount=i;break}}catch(t){this.fwd={id:e,loading:!1,nodes:[],total:0,error:String(t&&t.message||t)}}}},backForward(){this.fwd=this.fwdStack.pop()||null},closeForward(){this.fwd=null,this.fwdStack=[]},fwdParts(e){return sn({segs:e&&e.segs||[]}).parts},fwdImgs(e){return(e&&e.media||[]).filter(t=>t.kind==="image"&&t.local)},fwdOther(e){return(e&&e.media||[]).filter(t=>t.kind!=="image"&&t.local)},openCtx(e,t){this.menu={x:e.clientX,y:e.clientY,m:t}},canRecall(e){return!!(e&&e.msg_id&&e.role==="assistant"&&!e.recalled)},copyMsg(e){let t=String(e&&(e.text||(e.segs||[]).map(i=>(i.data||{}).text||"").join(""))||"");try{navigator.clipboard.writeText(t),this.toast("\u5DF2\u590D\u5236")}catch{this.toast("\u590D\u5236\u5931\u8D25\uFF08\u6D4F\u89C8\u5668\u4E0D\u5141\u8BB8\uFF09")}this.menu=null},async doRecall(e){if(this.menu=null,!(!e||!e.msg_id))try{await at("qqbot.chat.recall",{msg_id:e.msg_id}),e.recalled=1,this.toast("\u5DF2\u64A4\u56DE")}catch(t){this.toast(String(t&&t.message||t))}},jump(e){let t=String(e||"");if(!t)return;let i=t.replace(/"/g,'\\"'),s=document.querySelector('.rcq-im [data-msgid="'+i+'"]')||document.querySelector('.rcq-im [data-mid="'+i+'"]');if(!s){this.toast("\u88AB\u5F15\u7528\u7684\u6D88\u606F\u4E0D\u5728\u5F53\u524D\u9875");return}s.scrollIntoView({block:"center",behavior:"smooth"}),s.classList.add("im-flash"),setTimeout(()=>s.classList.remove("im-flash"),1200)},toast(e){this.toastMsg=String(e||""),clearTimeout(this._tt),this._tt=setTimeout(()=>{this.toastMsg=""},1800)},scheduleRead(){clearTimeout(this._rt),this._rt=setTimeout(()=>{W.msgs.length&&Zd(W.sid,W.msgs[W.msgs.length-1].id)},1200)},avatarOf(e){return e&&e.avatar?e.avatar:""},initialOf(e){return String(e&&(e.display||e.target_id)||"?").trim().slice(0,1)},pick(e){!e||e.session_id===W.sid||(e.unread=0,ds(e.session_id).then(()=>{this.readAt=Sr(e.session_id),this.$nextTick(()=>this.toBottom(!1)),this.scheduleRead(),this.schedulePendingRefresh()}))},toBottom(e=!0){let t=this.$refs.flow;t&&(t.scrollTo({top:t.scrollHeight,behavior:e?"smooth":"auto"}),W.atBottom=!0,this.showJump=!1)},async onScroll(){let e=this.$refs.flow;if(!e)return;let t=e.scrollHeight-e.scrollTop-e.clientHeight<40;if(W.atBottom=t,this.showJump=!t,e.scrollTop<160&&W.hasMore&&!W.loadingMore){let i=e.scrollHeight,s=e.scrollTop;await tn(!0),this.$nextTick(()=>{let n=this.$refs.flow;n&&(n.scrollTop=n.scrollHeight-i+s)})}},async reload(){await cs(),W.sid&&(await ds(W.sid),this.$nextTick(()=>this.toBottom(!1)))}},template:`
  <div class="rcq-im">
    <!-- rail -->
    <div class="im-rail">
      <div class="ava"><img v-if="S.uin" :src="'https://q1.qlogo.cn/g?b=qq&nk=' + S.uin + '&s=100'" alt="" /></div>
      <button v-for="it in railItems" :key="it.id" class="im-nav" :class="{ on: rail === it.id }"
        :title="it.title" @click="rail = it.id">
        <svg viewBox="0 0 24 24"><path :d="it.d" /></svg>
      </button>
      <div class="sp"></div>
    </div>

    <!-- \u4F1A\u8BDD\u5217\u8868 -->
    <div class="im-side" :style="{ width: sideWidth + 'px' }">
      <div class="im-side-h">
        <div class="im-search">
          <svg viewBox="0 0 24 24"><path d="M10 4a6 6 0 014.5 10.1l4.2 4.2-1.4 1.4-4.2-4.2A6 6 0 1110 4zm0 2a4 4 0 100 8 4 4 0 000-8z"/></svg>
          <input v-model="S.keyword" placeholder="\u641C\u7D22\u4F1A\u8BDD/\u6D88\u606F\u5185\u5BB9" @input="onKwInput" />
        </div>
        <button class="im-ico" title="\u5237\u65B0\u4F1A\u8BDD" @click="reload">
          <svg viewBox="0 0 24 24"><path d="M12 5V2L7 6l5 4V7a5 5 0 11-5 5H5a7 7 0 107-7z"/></svg>
        </button>
      </div>
      <div class="im-list">
        <div class="im-row" v-for="s in filtered" :key="s.session_id"
          :class="{ on: s.session_id === S.sid, muted: s.muted }" @click="pick(s)"
          @contextmenu.prevent="openSessMenu($event, s)">
          <div class="ava">
            <img v-if="avatarOf(s) && !badAva[s.session_id]" :src="avatarOf(s)" alt=""
              @error="badAva[s.session_id] = true" />
            <div v-else class="ava-t">{{ initialOf(s) }}</div>
            <span class="pin" v-if="s.pinned" title="\u5DF2\u7F6E\u9876">
              <svg viewBox="0 0 24 24"><path d="M16 9V4h1a1 1 0 000-2H7a1 1 0 000 2h1v5c0 1.66-1.34 3-3 3v2h5v7l1 1 1-1v-7h5v-2c-1.66 0-3-1.34-3-3z"/></svg>
            </span>
          </div>
          <div class="main">
            <div class="top">
              <div class="nm">{{ s.display || s.target_id }}</div>
              <div class="tm">{{ fmtListTime(s.last_at) }}</div>
            </div>
            <div class="pv">
              <template v-if="s.preview">
                <span v-if="s.preview_who" class="pv-who">{{ s.preview_who }}\uFF1A</span>{{ s.preview }}
              </template>
              <template v-else>{{ s.msg_count || 0 }} \u6761\u6D88\u606F</template>
            </div>
          </div>
          <span class="badge" v-if="s.unread && !s.muted">{{ s.unread > 99 ? '99+' : s.unread }}</span>
          <span class="dot" v-else-if="s.unread && s.muted"></span>
        </div>
        <div class="im-empty" v-if="!filtered.length">
          {{ S.keyword ? '\u6CA1\u6709\u5339\u914D\u7684\u4F1A\u8BDD' : '\u8FD8\u6CA1\u6709\u804A\u5929\u8BB0\u5F55' }}
        </div>
      </div>
    </div>

    <!-- \u804A\u5929\u533A -->
    <div class="im-chat">
      <div class="im-head">
        <div class="tt">{{ (cur && (cur.display || cur.target_id)) || '\u9009\u62E9\u4E00\u4E2A\u4F1A\u8BDD' }}</div>
        <div class="sub" v-if="cur">{{ fmtNum(total) }} \u6761</div>
        <div class="sp"></div>
        <div class="im-hsearch" v-if="searchOpen">
          <svg viewBox="0 0 24 24"><path d="M10 4a6 6 0 014.5 10.1l4.2 4.2-1.4 1.4-4.2-4.2A6 6 0 1110 4zm0 2a4 4 0 100 8 4 4 0 000-8z"/></svg>
          <input ref="msgSearch" :value="msgKw" placeholder="\u641C\u7D22\u672C\u4F1A\u8BDD\u7684\u6D88\u606F"
            @input="onSearch($event.target.value)" />
          <button v-if="msgKw" class="im-hclear" title="\u6E05\u9664" @click="onSearch('')">\xD7</button>
        </div>
        <button class="im-ico" :title="rpCfg.enabled ? '\u968F\u673A\u6311\u4E00\u6761\u7FA4\u91CC\u7684\u6D88\u606F\uFF0C\u8BA9\u673A\u5668\u4EBA\u56DE\u5B83' : '\u968F\u673A\u6311\u6D88\u606F\u56DE\u5DF2\u5173\u95ED\uFF08\u8BBE\u7F6E \u2192 \u80FD\u529B\uFF09'"
          @click="openRandom">
          <svg viewBox="0 0 24 24"><path d="M12 2l2.2 5.6L20 9l-4.6 3.4L16.6 18 12 14.9 7.4 18l1.2-5.6L4 9l5.8-1.4L12 2z"/></svg>
        </button>
        <button class="im-ico" title="\u641C\u7D22\u672C\u4F1A\u8BDD\u6D88\u606F" @click="toggleSearch">
          <svg viewBox="0 0 24 24"><path d="M10 4a6 6 0 014.5 10.1l4.2 4.2-1.4 1.4-4.2-4.2A6 6 0 1110 4zm0 2a4 4 0 100 8 4 4 0 000-8z"/></svg>
        </button>
        <button class="im-ico" title="\u5237\u65B0" @click="reload">
          <svg viewBox="0 0 24 24"><path d="M12 5V2L7 6l5 4V7a5 5 0 11-5 5H5a7 7 0 107-7z"/></svg>
        </button>
      </div>

      <div class="im-flow" ref="flow" @scroll="onScroll">
        <div class="im-srch" v-if="S.msgKeyword">
          \u641C\u7D22\u300C{{ S.msgKeyword }}\u300D\u627E\u5230 {{ S.msgs.length }} \u6761
          <button class="im-hclear" @click="onSearch(''); msgKw = ''">\u6E05\u9664</button>
        </div>
        <div class="im-more" v-if="S.loadingMore">\u52A0\u8F7D\u66F4\u65E9\u7684\u6D88\u606F\u2026</div>
        <div class="im-more" v-else-if="!S.hasMore && S.msgs.length >= 50">\u5DF2\u7ECF\u5230\u6700\u65E9\u4E86</div>
        <div class="im-empty" v-if="!S.msgs.length && !S.loading">
          {{ cur ? '\u8FD9\u4E2A\u4F1A\u8BDD\u8FD8\u6CA1\u6709\u6D88\u606F' : '\u5DE6\u8FB9\u9009\u4E00\u4E2A\u4F1A\u8BDD' }}
        </div>
        <template v-for="r in rows" :key="r.key">
          <div class="im-sys" v-if="r.type === 'sys'"><span>{{ r.text }}</span></div>
          <template v-else>
            <div class="im-divider" v-if="r.divider">\u4EE5\u4E0B\u4E3A\u65B0\u6D88\u606F</div>
            <im-message-row :m="r.m" :compact="r.compact" :show-time="r.showTime"
              @ctx="openCtx" @copy="copyMsg" @recall="doRecall" @jump="jump"
              @forward="openForward" />
          </template>
        </template>
      </div>

      <button class="im-jump" v-if="showJump" title="\u56DE\u5230\u6700\u65B0" @click="toBottom(true)">
        <svg viewBox="0 0 24 24"><path d="M12 16l-6-6 1.4-1.4L12 13.2l4.6-4.6L18 10l-6 6z"/></svg>
      </button>

      <!-- \u5408\u5E76\u8F6C\u53D1\u5C55\u5F00\u62BD\u5C49 -->
      <div class="im-fwd" v-if="fwd">
        <div class="fh">
          <button class="im-ico" v-if="fwdStack.length" title="\u8FD4\u56DE\u4E0A\u4E00\u5C42" @click="backForward">
            <svg viewBox="0 0 24 24"><path d="M15.4 7.4L14 6l-6 6 6 6 1.4-1.4-4.6-4.6z"/></svg>
          </button>
          <div class="ft">
            \u5408\u5E76\u8F6C\u53D1<template v-if="fwd.total"> \xB7 {{ fwd.total }} \u6761</template>
          </div>
          <button class="im-ico" title="\u5173\u95ED" @click="closeForward">
            <svg viewBox="0 0 24 24"><path d="M6.4 5L5 6.4 10.6 12 5 17.6 6.4 19 12 13.4 17.6 19 19 17.6 13.4 12 19 6.4 17.6 5 12 10.6 6.4 5z"/></svg>
          </button>
        </div>
        <div class="fb">
          <div class="im-more" v-if="fwd.loading">\u6B63\u5728\u5C55\u5F00\u2026</div>
          <div class="im-empty" v-else-if="fwd.error">{{ fwd.error }}</div>
          <div class="im-empty" v-else-if="!fwd.nodes.length">\u6CA1\u6709\u53EF\u663E\u793A\u7684\u5185\u5BB9</div>
          <div class="fn" v-for="(n,i) in fwd.nodes" :key="i">
            <div class="fn-h">
              <img class="fava" v-if="n.sender_id"
                :src="'https://q1.qlogo.cn/g?b=qq&nk=' + n.sender_id + '&s=100'" alt="" />
              <span class="fnm">{{ n.sender_name }}</span>
              <span class="ftm">{{ fmtListTime(n.time) }}</span>
            </div>
            <div class="fn-b">
              <span v-for="(p,pi) in fwdParts(n)" :key="pi">
                <span v-if="p.t === 'text'">{{ p.v }}</span>
                <span v-else-if="p.t === 'at'" class="at">{{ p.v }}</span>
                <img v-else-if="p.t === 'face'" class="face" :src="faceUrl(p.v)" alt="[\u8868\u60C5]" />
              </span>
              <div class="im-grid" :class="gridCls(fwdImgs(n).length)" v-if="fwdImgs(n).length">
                <img v-for="(m,mi) in fwdImgs(n)" :key="mi" :src="mediaUrl(m)" loading="lazy" alt="\u56FE\u7247" />
              </div>
              <div class="fn-f" v-for="(m,mi) in fwdOther(n)" :key="'f'+mi">
                {{ m.name || m.kind }} \xB7 {{ bytes(m.bytes) }}
              </div>
              <button class="fn-nested" v-if="n.nested" @click="openForward(n.nested)">
                \uFF08\u8FD9\u6761\u91CC\u8FD8\u5D4C\u5957\u4E86\u4E00\u4E2A\u5408\u5E76\u8F6C\u53D1\uFF0C\u70B9\u51FB\u5C55\u5F00\uFF09
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- \u968F\u673A\u6311\u4E00\u6761\u56DE\u590D -->
      <div class="im-rnd" v-if="rnd">
        <div class="fh">
          <div class="ft">\u968F\u673A\u6311\u4E00\u6761\u56DE\u590D</div>
          <button class="scope" title="\u5207\u6362\u6311\u9009\u8303\u56F4" @click="switchScope">
            {{ scopeLabel(rnd.scope) }}
          </button>
          <button class="im-ico" title="\u5173\u95ED" @click="closeRandom">
            <svg viewBox="0 0 24 24"><path d="M6.4 5L5 6.4 10.6 12 5 17.6 6.4 19 12 13.4 17.6 19 19 17.6 13.4 12 19 6.4 17.6 5 12 10.6 6.4 5z"/></svg>
          </button>
        </div>
        <div class="fb">
          <div class="im-more" v-if="rnd.loading">\u6B63\u5728\u6311\u2026</div>
          <div class="im-empty" v-else-if="rnd.error">{{ rnd.error }}</div>
          <template v-else-if="rnd.picked">
            <div class="rnd-hint">\u4ECE\u5DF2\u542F\u7528\u7684\u7FA4\u804A\u91CC\u968F\u673A\u7FFB\u4E86\u4E00\u6761\u51FA\u6765\uFF0C\u8BA9\u673A\u5668\u4EBA\u5BF9\u5B83\u8BF4\u70B9\u4EC0\u4E48\u3002\u6EE1\u610F\u5C31\u70B9\u300C\u53D1\u9001\u5230 QQ\u300D\u3002</div>
            <div class="rnd-pick">
              <div class="rnd-pick-h">
                <span class="rnd-who">{{ rnd.picked.sender_name || rnd.picked.sender_id }}</span>
                <span class="rnd-where">{{ rnd.picked.title || rnd.picked.target_id }}</span>
                <span class="rnd-time">{{ fmtListTime(rnd.picked.created_at) }}</span>
              </div>
              <div class="rnd-text">{{ rnd.picked.text }}</div>
            </div>
            <div class="rnd-arrow">\u2193 \u673A\u5668\u4EBA\u8FD9\u6837\u56DE</div>
            <div class="rnd-reply">{{ rnd.reply }}</div>
            <div class="rnd-foot" v-if="rnd.provider">\u7528 {{ rnd.provider }} \u751F\u6210</div>
            <div class="rnd-sent" v-if="rnd.sent"
              :class="rnd.sent.indexOf('\u5931\u8D25') >= 0 ? 'bad' : 'ok'">{{ rnd.sent }}</div>
          </template>
          <div class="im-empty" v-else>\u6CA1\u6709\u53EF\u6311\u7684\u6D88\u606F</div>
        </div>
        <div class="rf">
          <button class="primary" :disabled="rnd.loading || rnd.sending || !rnd.token"
            @click="sendRandom">{{ rnd.sending ? '\u53D1\u9001\u4E2D\u2026' : '\u53D1\u9001\u5230 QQ' }}</button>
          <button :disabled="rnd.loading" @click="pickRandom">\u6362\u4E00\u4E2A</button>
          <button @click="closeRandom">\u5173\u95ED</button>
        </div>
      </div>

      <!-- \u53EA\u8BFB\u680F\uFF1A\u672C\u9875\u4E0D\u63D0\u4F9B\u901A\u7528\u53D1\u9001\u5165\u53E3\uFF08\u968F\u673A\u6311\u56DE\u590D\u53EF\u5355\u72EC\u53D1\u5230 QQ\uFF09 -->
      <div class="im-readonly">
        <svg viewBox="0 0 24 24"><path d="M12 5c-5 0-9 4.5-10 7 1 2.5 5 7 10 7s9-4.5 10-7c-1-2.5-5-7-10-7zm0 11a4 4 0 110-8 4 4 0 010 8z"/></svg>
        <span>\u53EA\u8BFB\u6A21\u5F0F \xB7 \u672C\u9875\u4EC5\u7528\u4E8E\u6D4F\u89C8\u6D88\u606F\uFF1B\u{1F3B2} \u968F\u673A\u6311\u7684\u56DE\u590D\u53EF\u624B\u52A8\u53D1\u5230 QQ</span>
      </div>
    </div>

    <div class="im-menu" v-if="menu" :style="{ left: menu.x + 'px', top: menu.y + 'px' }"
      @click.stop>
      <button @click="copyMsg(menu.m)">\u590D\u5236\u6587\u5B57</button>
      <button v-if="canRecall(menu.m)" @click="doRecall(menu.m)">\u64A4\u56DE</button>
    </div>

    <div class="im-menu" v-if="sessMenu" :style="{ left: sessMenu.x + 'px', top: sessMenu.y + 'px' }"
      @click.stop>
      <button @click="togglePin(sessMenu.s)">{{ sessMenu.s.pinned ? '\u53D6\u6D88\u7F6E\u9876' : '\u7F6E\u9876\u8BE5\u4F1A\u8BDD' }}</button>
      <button @click="toggleMute(sessMenu.s)">{{ sessMenu.s.muted ? '\u53D6\u6D88\u514D\u6253\u6270' : '\u6D88\u606F\u514D\u6253\u6270' }}</button>
      <button @click="markReadNow(sessMenu.s)">\u6807\u8BB0\u4E3A\u5DF2\u8BFB</button>
      <button @click="exportSession(sessMenu.s)">\u5BFC\u51FA\u4F1A\u8BDD JSON</button>
      <button @click="clearSession(sessMenu.s)">\u6E05\u7A7A\u4F1A\u8BDD\u2026</button>
    </div>

    <div class="im-toast" v-if="toastMsg">{{ toastMsg }}</div>
  </div>`};var cp="rcq-im-style",Am=`
.rcq-im{
  --im-bg:var(--bg,#f5f6f7);
  --im-rail:var(--surface-2,#eceef0);
  --im-list:var(--surface,#fff);
  --im-chat:var(--bg,#f5f6f7);
  --im-input:var(--surface,#fff);
  --im-line:var(--border,#e3e5e8);
  --im-t1:var(--text,#1a1a1a);
  --im-t2:var(--text-muted,#6b7280);
  --im-t3:var(--text-faint,#9aa1a9);
  --im-hover:var(--surface-2,#f0f1f3);
  --im-active:var(--surface-3,#e7e9ec);
  --im-self:var(--ac,#0099ff);
  --im-self-t:#fff;
  --im-other:var(--surface,#fff);
  --im-r:12px;
  --im-shadow:0 6px 24px rgba(0,0,0,.14);
  position:relative;display:flex;
  height:calc(100vh - 152px);min-height:420px;
  background:var(--im-chat);color:var(--im-t1);
  border:1px solid var(--im-line);border-radius:14px;overflow:hidden;
  box-shadow:var(--shadow-sm,0 8px 24px rgba(0,0,0,.16));
  font-family:system-ui,-apple-system,"Microsoft YaHei UI","PingFang SC","Segoe UI",sans-serif;
  font-size:14px;line-height:1.5;
}
.rcq-im *{box-sizing:border-box}
.rcq-im ::-webkit-scrollbar{width:8px;height:8px}
.rcq-im ::-webkit-scrollbar-thumb{background:var(--im-active);border-radius:4px}
.rcq-im ::-webkit-scrollbar-track{background:transparent}

/* ---------------- \u5DE6\u4FA7 rail ---------------- */
.im-rail{width:54px;flex:none;background:var(--im-rail);display:flex;flex-direction:column;
  align-items:center;padding:12px 0 10px;gap:4px;border-right:1px solid var(--im-line)}
.im-rail .ava{width:36px;height:36px;border-radius:8px;overflow:hidden;background:var(--im-active);
  margin-bottom:8px;flex:none}
.im-rail .ava img{width:100%;height:100%;object-fit:cover;display:block}
.im-nav{width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;
  color:var(--im-t2);cursor:pointer;position:relative;border:none;background:none;padding:0}
.im-nav:hover{background:var(--im-hover);color:var(--im-t1)}
.im-nav.on{background:var(--im-active);color:var(--im-self)}
.im-nav.on::before{content:"";position:absolute;left:-8px;top:9px;bottom:9px;width:3px;
  border-radius:0 3px 3px 0;background:var(--im-self)}
.im-nav svg{width:22px;height:22px;fill:currentColor}
.im-rail .sp{flex:1}

/* ---------------- \u4F1A\u8BDD\u5217\u8868 ---------------- */
.im-side{width:268px;flex:none;background:var(--im-list);display:flex;flex-direction:column;
  border-right:1px solid var(--im-line);min-width:0}
.im-side-h{padding:12px 12px 8px;display:flex;gap:8px;align-items:center}
.im-search{flex:1;height:32px;border-radius:8px;background:var(--im-hover);display:flex;
  align-items:center;gap:6px;padding:0 10px;color:var(--im-t3)}
.im-search input{flex:1;border:none;background:none;outline:none;font-size:13px;color:var(--im-t1);
  font-family:inherit;min-width:0}
.im-search svg{width:14px;height:14px;fill:currentColor;flex:none}
.im-list{flex:1;overflow-y:auto;overflow-x:hidden;padding:0 8px 8px}
.im-row{display:flex;gap:10px;padding:9px 8px;border-radius:10px;cursor:pointer;align-items:center;
  margin-bottom:2px;transition:background .12s ease}
.im-row:hover{background:var(--im-hover)}
.im-row.on{background:var(--im-active)}
.im-row .ava{width:40px;height:40px;border-radius:8px;background:var(--im-active);flex:none;
  position:relative}
.im-row .ava img{width:100%;height:100%;object-fit:cover;display:block;border-radius:8px}
/* \u7F6E\u9876\u5C0F\u65D7\u6807\uFF08QQ \u5728\u5934\u50CF\u53F3\u4E0A\u89D2\uFF09 */
.im-row .pin{position:absolute;right:-3px;top:-3px;width:15px;height:15px;border-radius:50%;
  background:var(--im-self);display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 0 2px var(--im-list)}
.im-row .pin svg{width:9px;height:9px;fill:#fff}
/* \u672A\u8BFB\uFF1A\u7EA2\u70B9 / \u6570\u5B57\u6C14\u6CE1 */
.im-row .badge{min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:#f5534f;
  color:#fff;font-size:11px;line-height:18px;text-align:center;flex:none}
.im-row .dot{width:8px;height:8px;border-radius:50%;background:#f5534f;flex:none}
.im-row.muted .nm{font-weight:400;color:var(--im-t2)}
.ava-t{width:100%;height:100%;display:flex;align-items:center;justify-content:center;
  background:var(--im-active);color:var(--im-t2);font-size:15px;font-weight:600}
.im-row .main{flex:1;min-width:0}
.im-row .top{display:flex;gap:8px;align-items:baseline}
.im-row .nm{flex:1;font-size:14px;font-weight:500;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.im-row .tm{font-size:11px;color:var(--im-t3);flex:none}
.im-row .pv-who{color:var(--im-t3)}
.im-row .pv{font-size:12.5px;color:var(--im-t2);overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap;margin-top:2px}
.im-row .bdg{min-width:16px;height:16px;padding:0 4px;border-radius:8px;background:#f5534f;color:#fff;
  font-size:11px;line-height:16px;text-align:center;flex:none}
.im-empty{padding:40px 16px;text-align:center;color:var(--im-t3);font-size:12.5px}

/* ---------------- \u804A\u5929\u533A ---------------- */
.im-chat{flex:1;display:flex;flex-direction:column;min-width:0;background:transparent;position:relative}
.im-head{height:54px;flex:none;display:flex;align-items:center;gap:10px;padding:0 16px;
  border-bottom:1px solid var(--im-line);background:var(--im-list)}
.im-head .tt{font-size:15px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.im-head .sub{font-size:12px;color:var(--im-t3);flex:none}
.im-head .sp{flex:1}
.im-ico{width:30px;height:30px;border-radius:6px;border:none;background:none;color:var(--im-t2);
  cursor:pointer;display:flex;align-items:center;justify-content:center}
.im-ico:hover{background:var(--im-hover);color:var(--im-t1)}
.im-ico svg{width:17px;height:17px;fill:currentColor}

.im-flow{flex:1;overflow-y:auto;overflow-x:hidden;padding:14px 20px 8px;scroll-behavior:auto}
.im-flow.pad{padding-bottom:0}
.im-time{text-align:center;margin:12px 0 10px;font-size:12px;color:var(--im-t3)}
.im-sys{text-align:center;margin:8px 0;font-size:12px;color:var(--im-t3)}
.im-sys span{display:inline-block;padding:2px 8px;border-radius:6px;background:var(--im-hover)}

.im-msg{display:flex;gap:10px;margin-bottom:10px;align-items:flex-start;position:relative}
.im-msg.compact{margin-top:-4px;margin-bottom:8px}
.im-msg.me{flex-direction:row-reverse}
.im-msg .ava{width:34px;height:34px;border-radius:6px;overflow:hidden;background:var(--im-active);flex:none}
.im-msg .ava img{width:100%;height:100%;object-fit:cover;display:block}
.im-msg .ava.ph{visibility:hidden}
.im-msg .col{max-width:min(70%,560px);min-width:0;display:flex;flex-direction:column}
.im-msg.me .col{align-items:flex-end}
.im-msg .who{font-size:12px;color:var(--im-t3);margin:0 2px 3px}
.im-bub{position:relative;background:var(--im-other);border-radius:var(--im-r);
  border:1px solid var(--im-line);
  padding:8px 12px;color:var(--im-t1);word-break:break-word;white-space:pre-wrap;
  box-shadow:0 1px 2px rgba(0,0,0,.05)}
.im-msg.me .im-bub{background:var(--im-self);color:var(--im-self-t);border-color:transparent;
  border-bottom-right-radius:4px}
.im-msg:not(.me) .im-bub{border-bottom-left-radius:4px}
.im-bub.media{padding:4px;background:transparent;box-shadow:none}
.im-msg.me .im-bub.media{background:transparent}
.im-bub .at{color:var(--im-self);font-weight:500}
.im-msg.me .im-bub .at{color:#fff;text-decoration:underline}
.im-bub img.face{width:20px;height:20px;vertical-align:-4px;margin:0 1px}
.im-quote{border-left:3px solid var(--im-active);padding:4px 8px;margin-bottom:6px;
  font-size:12.5px;color:var(--im-t2);background:rgba(0,0,0,.03);border-radius:4px;
  max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.im-msg.me .im-quote{background:rgba(255,255,255,.16);color:rgba(255,255,255,.9);
  border-left-color:rgba(255,255,255,.5)}
.im-recall{font-size:12px;color:var(--im-t3);font-style:italic}
/* \u64A4\u56DE\u6807\u8BB0\uFF1A\u5185\u5BB9\u7167\u5E38\u663E\u793A\uFF0C\u53EA\u662F\u6DE1\u4E00\u70B9 + \u4E00\u4E2A\u89D2\u6807 */
.im-msg.recalled .im-bub{opacity:.62}
.im-msg.recalled .im-grid,.im-msg.recalled .im-video{opacity:.62}
.im-rec-tag{display:inline-block;margin-left:6px;font-size:10.5px;color:#e8a33d;
  border:1px solid #e8a33d;border-radius:999px;padding:0 6px;vertical-align:1px}
.im-meta{font-size:11px;color:var(--im-t3);margin-top:3px;padding:0 2px}

/* \u5A92\u4F53 */
.im-grid{display:grid;gap:4px;max-width:420px}
.im-grid.g1{grid-template-columns:1fr}
.im-grid.g2{grid-template-columns:repeat(2,1fr)}
.im-grid.g3{grid-template-columns:repeat(3,1fr)}
.im-grid img{width:100%;height:100%;object-fit:cover;border-radius:8px;display:block;cursor:zoom-in;
  background:var(--im-active);min-height:60px}
.im-grid.g1 img{max-height:320px;object-fit:contain;background:transparent}
.im-video{position:relative;max-width:420px;border-radius:8px;overflow:hidden;background:#000}
.im-video video{width:100%;max-height:320px;display:block}
.im-voice{display:flex;align-items:center;gap:8px;cursor:pointer;min-width:96px}
.im-voice .wave{display:flex;align-items:center;gap:2px;height:18px}
.im-voice .wave i{width:3px;background:currentColor;border-radius:2px;opacity:.55}
.im-voice .sec{font-size:12px;opacity:.8;flex:none}
.im-file{display:flex;gap:10px;align-items:center;min-width:200px}
.im-file .fi{width:34px;height:34px;border-radius:6px;background:rgba(0,0,0,.08);display:flex;
  align-items:center;justify-content:center;font-size:11px;font-weight:600;flex:none}
.im-card{min-width:220px;max-width:340px}
.im-card .ct{font-size:13.5px;font-weight:600;margin-bottom:2px}
.im-card .cd{font-size:12px;color:var(--im-t2);overflow:hidden;display:-webkit-box;
  -webkit-line-clamp:2;-webkit-box-orient:vertical}
.im-unk{font-size:12.5px;color:var(--im-t2)}
.im-unk .raw{margin-top:6px;font-family:ui-monospace,Menlo,monospace;font-size:11px;
  color:var(--im-t3);white-space:pre-wrap;max-height:120px;overflow:auto}

.im-jump{position:absolute;right:20px;bottom:150px;width:36px;height:36px;border-radius:50%;
  background:var(--im-list);border:1px solid var(--im-line);box-shadow:var(--im-shadow);
  display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--im-t2)}
.im-jump:hover{color:var(--im-t1)}
.im-jump svg{width:18px;height:18px;fill:currentColor}
.im-more{text-align:center;padding:8px;font-size:12px;color:var(--im-t3)}

.im-readonly{flex:none;border-top:1px solid var(--im-line);background:transparent;
  padding:8px 16px;display:flex;align-items:center;justify-content:center;gap:7px;
  font-size:12px;color:var(--im-t3);user-select:none}
.im-readonly svg{width:15px;height:15px;fill:currentColor;opacity:.8}

/* \u60AC\u505C\u64CD\u4F5C\u6761 / \u53F3\u952E\u83DC\u5355 / \u9AD8\u4EAE / \u672A\u8BFB\u5206\u5272 / \u5F15\u7528\u6761 / \u8F7B\u63D0\u793A */
.im-ops{position:absolute;top:-10px;right:6px;display:flex;gap:2px;opacity:0;
  transition:opacity .12s;background:var(--im-list);border:1px solid var(--im-line);
  border-radius:6px;padding:2px;box-shadow:0 2px 8px rgba(0,0,0,.08);z-index:2}
.im-msg:hover .im-ops{opacity:1}
.im-msg.me .im-ops{right:auto;left:6px}
.im-op{border:none;background:none;font-size:11px;color:var(--im-t2);cursor:pointer;
  padding:2px 6px;border-radius:4px;font-family:inherit}
.im-op:hover{background:var(--im-hover);color:var(--im-t1)}
.im-menu{position:fixed;z-index:960;background:var(--im-list);border:1px solid var(--im-line);
  border-radius:8px;box-shadow:var(--im-shadow);padding:4px;min-width:120px}
.im-menu button{display:block;width:100%;text-align:left;border:none;background:none;
  font-size:13px;color:var(--im-t1);padding:7px 10px;border-radius:5px;cursor:pointer;
  font-family:inherit}
.im-menu button:hover{background:var(--im-hover)}
.im-flash{animation:imflash 1.1s ease}
@keyframes imflash{0%,100%{background:transparent}30%{background:rgba(0,153,255,.14)}}
.im-divider{text-align:center;font-size:12px;color:var(--im-t3);margin:10px 0}
.im-toast{position:fixed;left:50%;bottom:130px;transform:translateX(-50%);z-index:970;
  background:rgba(0,0,0,.78);color:#fff;font-size:12.5px;padding:6px 14px;border-radius:16px}

/* \u968F\u673A\u6311\u4E00\u6761\u56DE\u590D\u7684\u62BD\u5C49 */
.im-rnd{position:absolute;top:0;right:0;bottom:0;width:390px;max-width:82%;
  background:var(--im-list);border-left:1px solid var(--im-line);z-index:6;
  display:flex;flex-direction:column;box-shadow:-6px 0 20px rgba(0,0,0,.07)}
.im-rnd .fh{flex:none;height:48px;display:flex;align-items:center;gap:8px;
  padding:0 10px 0 16px;border-bottom:1px solid var(--im-line)}
.im-rnd .ft{flex:1;font-size:14px;font-weight:600;color:var(--im-t1)}
.im-rnd .scope{font-size:11.5px;color:var(--im-t2);border:1px solid var(--im-line);
  background:var(--im-hover);border-radius:11px;padding:3px 10px;cursor:pointer;flex:none}
.im-rnd .scope:hover{color:var(--im-t1)}
.im-rnd .fb{flex:1;overflow:auto;padding:12px 14px 18px}
.im-rnd .rnd-hint{font-size:11.5px;color:var(--im-t3);margin-bottom:10px;line-height:1.6}
.im-rnd .rnd-pick{border:1px solid var(--im-line);border-radius:8px;padding:9px 11px;
  background:var(--im-hover)}
.im-rnd .rnd-pick-h{display:flex;align-items:center;gap:7px;margin-bottom:5px}
.im-rnd .rnd-who{font-size:12.5px;font-weight:600;color:var(--im-t1)}
.im-rnd .rnd-where{font-size:11px;color:var(--im-t3);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap;flex:1}
.im-rnd .rnd-time{font-size:11px;color:var(--im-t3);flex:none}
.im-rnd .rnd-text{font-size:13.5px;color:var(--im-t1);line-height:1.6;
  white-space:pre-wrap;word-break:break-word}
.im-rnd .rnd-arrow{font-size:11.5px;color:var(--im-t3);margin:14px 0 7px;text-align:center}
.im-rnd .rnd-reply{background:var(--im-self);border-radius:8px;padding:9px 11px;
  font-size:13.5px;line-height:1.6;color:var(--im-self-t);white-space:pre-wrap;word-break:break-word}
.im-rnd .rnd-foot{font-size:11px;color:var(--im-t3);margin-top:8px;text-align:right}
.im-rnd .rnd-sent{font-size:11.5px;margin-top:8px;padding:5px 9px;border-radius:6px;
  background:var(--im-hover);color:var(--im-t2)}
.im-rnd .rnd-sent.ok{color:var(--im-self)}
.im-rnd .rnd-sent.bad{color:#e5484d}
.im-rnd .rf{flex:none;display:flex;gap:8px;padding:10px 14px;
  border-top:1px solid var(--im-line)}
.im-rnd .rf button{flex:1;font-size:12.5px;border:1px solid var(--im-line);
  background:var(--im-hover);color:var(--im-t1);border-radius:6px;padding:7px 0;cursor:pointer}
.im-rnd .rf button:hover{background:var(--im-active)}
.im-rnd .rf button.primary{background:var(--im-self);border-color:var(--im-self);
  color:var(--im-self-t)}
.im-rnd .rf button.primary:hover{opacity:.88;background:var(--im-self)}
.im-rnd .rf button:disabled{opacity:.45;cursor:default}

/* \u5408\u5E76\u8F6C\u53D1\u5C55\u5F00\u62BD\u5C49 */
.im-fwd{position:absolute;top:0;right:0;bottom:0;width:390px;max-width:82%;
  background:var(--im-list);border-left:1px solid var(--im-line);z-index:6;
  display:flex;flex-direction:column;box-shadow:-6px 0 20px rgba(0,0,0,.07)}
.im-fwd .fh{flex:none;height:48px;display:flex;align-items:center;gap:8px;
  padding:0 10px 0 16px;border-bottom:1px solid var(--im-line)}
.im-fwd .ft{flex:1;font-size:14px;font-weight:600;color:var(--im-t1)}
.im-fwd .fb{flex:1;overflow:auto;padding:10px 14px 18px}
.im-fwd .fn{padding:9px 0;border-bottom:1px solid var(--im-line)}
.im-fwd .fn:last-child{border-bottom:none}
.im-fwd .fn-h{display:flex;align-items:center;gap:6px;margin-bottom:4px}
.im-fwd .fava{width:20px;height:20px;border-radius:4px;object-fit:cover;flex:none}
.im-fwd .fnm{font-size:12.5px;color:var(--im-t2);flex:1;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.im-fwd .ftm{font-size:11px;color:var(--im-t3)}
.im-fwd .fn-b{font-size:13.5px;color:var(--im-t1);line-height:1.5;word-break:break-word}
.im-fwd .fn-b .at{color:var(--im-self);font-weight:500}
.im-fwd .fn-b .face{width:18px;height:18px;vertical-align:-3px}
.im-fwd .fn-b .im-grid{margin-top:6px;max-width:100%}
.im-fwd .fn-f{font-size:11.5px;color:var(--im-t3);margin-top:5px}
.im-fwd .fn-nested{display:block;font-size:11.5px;color:var(--im-self);margin-top:5px;
  border:none;background:none;padding:0;cursor:pointer;font-family:inherit;text-align:left}
.im-card.fwd{cursor:pointer;padding:8px 12px;border:1px solid var(--im-line);
  border-radius:10px;background:var(--im-bg);transition:background .12s}
.im-card.fwd:hover{background:var(--im-hover)}

/* \u804A\u5929\u533A\u641C\u7D22\u6846\uFF08\u4F1A\u8BDD\u5185\u641C\u7D22\uFF09 */
.im-hsearch{display:flex;align-items:center;gap:6px;height:28px;padding:0 8px;
  border:1px solid var(--im-line);border-radius:14px;background:var(--im-bg);min-width:200px}
.im-hsearch svg{width:14px;height:14px;fill:var(--im-t3);flex:none}
.im-hsearch input{border:none;outline:none;background:none;font-family:inherit;
  font-size:12.5px;color:var(--im-t1);width:100%;min-width:0}
.im-hclear{border:none;background:none;cursor:pointer;color:var(--im-t3);
  font-size:15px;line-height:1;padding:0 2px;font-family:inherit}
.im-hclear:hover{color:var(--im-t1)}
.im-srch{position:sticky;top:0;z-index:3;background:var(--im-hover);color:var(--im-t2);
  font-size:12px;padding:6px 14px;display:flex;align-items:center;gap:8px;
  border-bottom:1px solid var(--im-line)}

/* \u5927\u56FE\u67E5\u770B */
.im-viewer{position:fixed;inset:0;z-index:950;background:rgba(0,0,0,.82);display:flex;
  align-items:center;justify-content:center;padding:24px;cursor:zoom-out}
.im-viewer img{max-width:100%;max-height:100%;border-radius:8px}
.im-viewer .x{position:absolute;top:16px;right:22px;color:#fff;font-size:26px;cursor:pointer;
  line-height:1;background:none;border:none}
`;function dp(){if(typeof document>"u"||document.getElementById(cp))return;let e=document.createElement("style");e.id=cp,e.textContent=Am,document.head.appendChild(e)}var Im="qqbot",pp="rcq-style",up="rcq.tab",Ir=null,yt=ui({toast:"",toastKind:"",conn:null}),ml=null;function D(e,t){yt.toast=String(e??""),yt.toastKind=t||"",ml&&clearTimeout(ml),ml=setTimeout(()=>{yt.toast=""},t==="err"?5200:2600)}async function Ue(e,t,i){if(!Ir||!Ir.invoke)throw new Error("\u63D2\u4EF6\u8FD0\u884C\u65F6\u672A\u5C31\u7EEA");return await Ir.invoke(e,t||{},i)}async function Y(e,t,i){let s=await Ue(e,t,i);return s&&typeof s=="object"&&"data"in s&&s.data!==null&&s.data!==void 0?s.data:s}function Z(e){return e?String(e&&e.message||e):"\u672A\u77E5\u9519\u8BEF"}var mi=e=>e<10?"0"+e:""+e;function Nm(e){if(!e)return"\u2014";let t=new Date(e*1e3);return t.getMonth()+1+"-"+mi(t.getDate())+" "+mi(t.getHours())+":"+mi(t.getMinutes())}function mp(e){if(!e)return"\u2014";let t=new Date(e*1e3);return t.getFullYear()+"-"+mi(t.getMonth()+1)+"-"+mi(t.getDate())+" "+mi(t.getHours())+":"+mi(t.getMinutes())+":"+mi(t.getSeconds())}function rn(e){return e==null||e===""||(e=Number(e),isNaN(e))?"\u2014":e>=1e6?(e/1e6).toFixed(1)+"M":e>=1e4?(e/1e4).toFixed(1)+"\u4E07":String(e)}function fl(e){return String(e||"").split(/[,，\s]+/).map(t=>t.trim()).filter(Boolean)}function fp(e){if(!e)return"";let t=e.abs||(e.rel?"/opt/rcbot/media/"+e.rel:"");return t?"/api/fm/preview?path="+encodeURIComponent(t):""}function vp(e){return!e||!e.local?!1:e.exists!==0}var vl=new Map,Em="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",gp={name:"ThumbImg",props:{rel:String,size:{type:Number,default:360}},data(){return{src:"",io:null}},computed:{blank(){return Em}},mounted(){let e=this.rel+"@"+this.size,t=vl.get(e);if(t){this.src=t;return}if(typeof IntersectionObserver>"u"){this.load();return}this.io=new IntersectionObserver(i=>{i.some(s=>s.isIntersecting)&&(this.io.disconnect(),this.io=null,this.load())},{rootMargin:"240px"}),this.io.observe(this.$el)},beforeUnmount(){this.io&&this.io.disconnect()},methods:{async load(){let e=this.rel+"@"+this.size,t=vl.get(e);if(t){this.src=t;return}try{let i=await Y("qqbot.chat.thumb",{rel:this.rel,size:this.size});if(i&&i.path){let s="/api/fm/preview?path="+encodeURIComponent(i.path);vl.set(e,s),this.src=s}}catch{}}},template:'<img :src="src || blank" decoding="async" alt="" />'},Om=`
.rcq{--t:var(--text);--m:var(--text-muted);--f:var(--text-faint);--bd:var(--border);
 --bd2:var(--border-strong);--sf:var(--surface);--sf2:var(--surface-2);--sf3:var(--surface-3);
 --ac:var(--accent);--acbg:var(--accent-soft);--ok:var(--success);--warn:var(--warning);
 --bad:var(--danger);--r:var(--radius-md);
 color:var(--t);font-size:13px;line-height:1.6;font-family:var(--font)}
.rcq *{box-sizing:border-box}

/* \u9876\u90E8\u9009\u9879\u5361\uFF08\u63D2\u4EF6\u5185\u552F\u4E00\u5BFC\u822A\uFF09\uFF1A\u80F6\u56CA\u5F0F\uFF0C\u6D3B\u52A8\u9879\u7528\u4E3B\u9898\u8272\u5E95 */
.rcq-bar{position:sticky;top:0;z-index:9;display:flex;align-items:center;gap:4px;flex-wrap:wrap;
 padding:5px 6px;background:var(--sf2);border:1px solid var(--bd);border-radius:12px;
 margin-bottom:14px;backdrop-filter:blur(8px)}
.rcq-tab{padding:6px 12px;font-size:13px;color:var(--m);cursor:pointer;user-select:none;
 border-radius:8px;white-space:nowrap;transition:background .12s,color .12s}
.rcq-tab:hover{color:var(--t);background:var(--sf3)}
.rcq-tab.on{color:var(--ac);background:var(--acbg);font-weight:600}
.rcq-bar-r{margin-left:auto;display:flex;align-items:center;gap:10px;padding:0 4px}
.rcq-lamp{display:inline-flex;align-items:center;gap:5px;font-size:11px;color:var(--m)}
.rcq-lamp b{width:7px;height:7px;border-radius:50%;background:var(--bd2);display:inline-block}
.rcq-lamp b.on{background:var(--ok);box-shadow:0 0 0 3px rgba(63,185,80,.16)}
.rcq-lamp b.off{background:var(--bad)}

/* \u5361\u7247 */
.rcq-pnl{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);
 padding:15px 17px;margin-bottom:12px}
.rcq-pnl.flat{padding:0}
.rcq-ph{display:flex;align-items:center;gap:8px;margin-bottom:12px;min-height:24px;flex-wrap:wrap}
.rcq-ph b{font-size:14px;font-weight:600;letter-spacing:.2px}
.rcq-ph .sp{margin-left:auto}
.rcq-sec{border-top:1px solid var(--bd);margin:12px -16px;padding:12px 16px 0}
/* .rcq-pnl.flat \u81EA\u8EAB padding \u4E3A 0\uFF0C\u8D1F\u8FB9\u8DDD\u4F1A\u628A\u5185\u5BB9\u9876\u5230\u8FB9\u6846\u4E0A\uFF08\u6982\u89C8\u7684\u300C\u7CFB\u7EDF\u4FE1\u606F\u300D\u5C31\u662F\uFF09\uFF0C
   \u8FD9\u79CD\u5361\u7247\u91CC\u7684\u5206\u9694\u6BB5\u6539\u6210\u6B63\u5E38\u5185\u8FB9\u8DDD\uFF0C\u5206\u9694\u7EBF\u4ECD\u7136\u6A2A\u8D2F\u6574\u5F20\u5361 */
.rcq-pnl.flat > .rcq-sec{margin-left:0;margin-right:0;padding:12px 16px 0}

/* \u952E\u503C */
.rcq-kv{display:grid;grid-template-columns:88px 1fr;gap:7px 12px;font-size:12.5px;align-items:baseline}
.rcq-kv .k{color:var(--m)}
.rcq-kv .v{color:var(--t);font-family:var(--font-mono);word-break:break-all}
.rcq-fld{display:flex;align-items:baseline;gap:7px;font-size:12.5px;min-width:0}
.rcq-fld .k{color:var(--m);flex:none}
.rcq-fld .v{color:var(--t);font-family:var(--font-mono);word-break:break-all}
.rcq-fld.full{grid-column:1/-1}
.rcq-row2{display:grid;grid-template-columns:1fr 1fr;gap:9px 16px;margin-top:9px}
.rcq-row2 > .full{grid-column:1/-1}

/* \u6982\u89C8\u4E09\u680F */
.rcq-ov{display:grid;grid-template-columns:minmax(230px,.95fr) minmax(0,1.5fr) 160px;
 gap:12px;align-items:start}
.rcq-ov > div > .rcq-pnl:last-child{margin-bottom:0}
.rcq-acct{display:flex;align-items:center;gap:12px;padding:16px}
.rcq-ava{width:52px;height:52px;border-radius:50%;object-fit:cover;flex:none;
 background:var(--sf2);border:1px solid var(--bd)}
.rcq-nick{font-size:14px;font-weight:600;display:flex;align-items:center;gap:7px}
.rcq-dot{width:7px;height:7px;border-radius:50%;background:var(--bd2);display:inline-block;flex:none}
.rcq-dot.on{background:var(--ok)}
.rcq-dot.off{background:var(--bad)}
.rcq-uin{font-size:11.5px;color:var(--m);font-family:var(--font-mono);margin-top:2px}

/* \u4EEA\u8868 */
.rcq-gauges{display:flex;flex-direction:column;gap:12px}
.rcq-gauge{position:relative;display:flex;align-items:center;justify-content:center;
 padding:12px 6px;background:var(--sf);border:1px solid var(--bd);border-radius:var(--r)}
.rcq-gauge svg{width:96px;height:96px;display:block}
.rcq-gauge .lbl{position:absolute;inset:0;display:flex;flex-direction:column;
 align-items:center;justify-content:center;pointer-events:none}
.rcq-gauge .lbl b{font-size:17px;font-weight:700;line-height:1.1}
.rcq-gauge .lbl span{font-size:10px;color:var(--m);margin-top:1px}

/* \u8BA1\u6570\u6761 */
.rcq-counters{display:grid;grid-template-columns:repeat(5,1fr);background:var(--sf);
 border:1px solid var(--bd);border-radius:var(--r);overflow:hidden;margin-bottom:12px}
.rcq-ct{padding:13px 6px;text-align:center;border-left:1px solid var(--bd)}
.rcq-ct:first-child{border-left:0}
.rcq-ct b{display:block;font-size:23px;font-weight:700;line-height:1.2}
.rcq-ct span{font-size:11px;color:var(--m)}

/* \u5217\u8868 */
.rcq-list{display:flex;flex-direction:column}
.rcq-row{display:flex;align-items:center;gap:10px;padding:10px 16px;border-top:1px solid var(--bd);
 cursor:default}
.rcq-row:first-child{border-top:0}
.rcq-row.click{cursor:pointer}
.rcq-row.click:hover,.rcq-row.on{background:var(--sf2)}
.rcq-row .main{flex:1;min-width:0}
.rcq-row .t{font-size:12.5px;font-weight:600;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.rcq-row .d{font-size:11.5px;color:var(--m);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:1px}
.rcq-row .acts{display:flex;gap:6px;flex:none;align-items:center}
/* \u4F1A\u8BDD\u5217\u8868\u884C\u5185\u7684\u542F\u7528\u5F00\u5173\uFF1A\u5782\u76F4\u5C45\u4E2D\u3001\u4E0D\u6491\u9AD8\u884C\u9AD8 */
.rcq-row .acts .switch{margin:0;display:inline-flex;align-items:center}
.rcq-row .acts .switch input{width:30px;height:17px}
.rcq-mono{font-family:var(--font-mono);font-size:11.5px}

.rcq-empty{padding:38px 12px;text-align:center;color:var(--f);font-size:12.5px}
.rcq-empty b{display:block;font-size:24px;margin-bottom:6px;opacity:.45;font-weight:400}

/* \u4E8C\u7EF4\u7801 */
.rcq-qr{width:196px;height:196px;background:#fff;border:1px solid var(--bd);
 border-radius:var(--r);padding:9px;display:flex;align-items:center;justify-content:center;flex:none}
.rcq-qr svg{width:100%;height:100%;display:block}
.rcq-qr .ph{color:#999;font-size:12px;text-align:center;padding:0 10px}

/* \u65E5\u5FD7\uFF08SnowLuma \u5BB9\u5668\u65E5\u5FD7\uFF1A\u7EAF\u6587\u672C\u884C\uFF0C\u6309\u7EA7\u522B\u7740\u8272\uFF09 */
.rcq-log{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);
 padding:11px 13px;font-family:var(--font-mono);font-size:11.5px;line-height:1.85;
 max-height:min(64vh,640px);overflow:auto;white-space:pre-wrap;word-break:break-word}
/* \u7EA7\u522B\u7C7B\u540D\u4E00\u5F8B\u52A0 rcq-lv- \u524D\u7F00\uFF1A\u9762\u677F\u5168\u5C40\u6709 .error{padding:24px;text-align:center}\uFF0C
   \u76F4\u63A5\u5199 class="error" \u4F1A\u628A\u65E5\u5FD7\u884C\u641E\u6210\u5C45\u4E2D\u7684\u5927\u5757 */
.rcq-ln{color:var(--t);padding:0;text-align:left}
.rcq-ln .lv{font-weight:700;margin-right:5px}
.rcq-ln.rcq-lv-info .lv{color:var(--m)}
.rcq-ln.rcq-lv-debug{color:var(--f)}
.rcq-ln.rcq-lv-debug .lv{color:var(--f)}
.rcq-ln.rcq-lv-warn{color:var(--warn)}
.rcq-ln.rcq-lv-error{color:var(--bad)}
.rcq-ln.rcq-lv-fatal{color:var(--bad);font-weight:600}
.rcq-pill{display:inline-flex;align-items:center;gap:5px;padding:2px 9px;font-size:11px;
 border:1px solid var(--bd2);border-radius:999px;color:var(--m);white-space:nowrap}
.rcq-pill.ok{color:var(--ok);border-color:var(--ok)}
.rcq-pill.off{color:var(--bad);border-color:var(--bad)}
.rcq-qr-ok{display:flex;flex-direction:column;align-items:center;justify-content:center;
 gap:6px;color:var(--ok);font-size:12.5px;text-align:center;width:100%;height:100%}
.rcq-qr-ok b{font-size:30px;font-weight:400;line-height:1}

/* \u8868\u5355 */
.rcq-form{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.rcq-fi{display:flex;flex-direction:column;gap:5px;min-width:0}
.rcq-fi > span{font-size:11.5px;color:var(--m)}
.rcq-fi.wide{grid-column:1/-1}
.rcq-fi > .switch{align-self:flex-start;margin-top:3px}
.rcq-fi > .rcq-num{max-width:220px}
.rcq-ta{width:100%;min-height:132px;resize:vertical;padding:9px 11px;font-size:12.5px;
 line-height:1.7;font-family:var(--font-mono);color:var(--t);background:var(--surface);
 border:1px solid var(--bd);border-radius:var(--r)}
.rcq-ta:focus{outline:none;border-color:var(--ac);box-shadow:var(--ring)}
.rcq-note{font-size:11px;color:var(--f);margin-top:4px;line-height:1.55}
/* \u62A5\u9519\u539F\u6587\u53EF\u80FD\u5F88\u957F\uFF08\u6A21\u578B\u8FD4\u56DE\u7684 JSON\uFF09\uFF0C\u4E24\u884C\u622A\u65AD\uFF0C\u60AC\u505C\u770B\u5168\u6587 */
.rcq-err{color:var(--bad);white-space:normal;word-break:break-word;
 display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}

/* \u4F1A\u8BDD\u8BE6\u60C5 */
.rcq-msgs{max-height:min(46vh,460px);overflow:auto;padding:2px 0}
.rcq-msg{display:flex;gap:9px;padding:7px 0;border-top:1px dashed var(--bd)}
.rcq-msg:first-child{border-top:0}
.rcq-msg .who{flex:none;width:74px;font-size:11px;color:var(--m);text-align:right;
 overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rcq-msg .body{flex:1;min-width:0;font-size:12.5px;white-space:pre-wrap;word-break:break-word}
.rcq-msg.me .who{color:var(--ac)}
.rcq-bar2{height:6px;background:var(--sf3);border-radius:3px;overflow:hidden;margin-top:6px}
.rcq-bar2 i{display:block;height:100%;background:var(--ac);border-radius:3px}
.rcq-bar2 i.hi{background:var(--warn)}
.rcq-bar2 i.max{background:var(--bad)}

.rcq-split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:12px;align-items:start}
.rcq-flex{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.rcq-hint{font-size:11.5px;color:var(--m)}
.rcq-warn{border-color:var(--warn);color:var(--warn)}

/* ---- \u591A\u5B9E\u4F8B\uFF08QQ \u8D26\u6237\uFF09 ---- */
.rcq-inst{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
.rcq-icard{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:14px 15px}
.rcq-icard.on{border-color:var(--ac)}
.rcq-itop{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.rcq-itop .nm{flex:1;min-width:0}
.rcq-itop .nm b{display:block;font-size:13.5px;font-weight:600;overflow:hidden;
 text-overflow:ellipsis;white-space:nowrap}
.rcq-itop .nm span{font-size:11.5px;color:var(--m);font-family:var(--font-mono)}
.rcq-imeta{display:grid;grid-template-columns:auto 1fr;gap:4px 10px;font-size:11.5px;
 margin-bottom:10px}
.rcq-imeta .k{color:var(--m)}
.rcq-imeta .v{font-family:var(--font-mono);word-break:break-all}
.rcq-iacts{display:flex;gap:6px;flex-wrap:wrap;align-items:center}


/* ---- \u5A92\u4F53\u5E93 ---- */
.rcq-mlib{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:10px}
.rcq-mcard{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);
 overflow:hidden;display:flex;flex-direction:column;position:relative}
.rcq-mcard.on{border-color:var(--ac);box-shadow:0 0 0 1px var(--ac)}
.rcq-mcard.gone{opacity:.55}
.rcq-mcard .ck{position:absolute;top:6px;left:6px;z-index:2;background:rgba(0,0,0,.45);
 border-radius:5px;padding:1px 5px;line-height:1.4}
.rcq-mcard .th{height:118px;background:var(--sf3);display:flex;align-items:center;
 justify-content:center;overflow:hidden;cursor:zoom-in;position:relative}
.rcq-mcard .th img{width:100%;height:100%;object-fit:cover;display:block}
.rcq-mcard .th video{width:100%;height:100%;object-fit:cover;display:block}
.rcq-mcard .th .ph{font-size:30px;opacity:.6}
.rcq-mcard .meta{padding:7px 9px;font-size:11px;color:var(--m);flex:1;min-width:0}
.rcq-mcard .meta .n{font-size:11.5px;color:var(--t);font-weight:600}
.rcq-mcard .meta .s,.rcq-mcard .meta .t{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rcq-mcard .dl{display:block;text-align:center;padding:5px;border-top:1px solid var(--bd);
 font-size:11px;color:var(--ac);text-decoration:none}
.rcq-mcard .dl:hover{background:var(--sf2)}
.rcq-mcard .dl.gone{color:var(--m);cursor:default}

/* \u9AA8\u67B6\u5C4F\uFF08\u9996\u5C4F\u52A0\u8F7D\u4E2D\u5360\u4F4D\uFF0C\u907F\u514D"\u767D\u5C4F + \u7A81\u7136\u51FA\u73B0"\uFF09 */
.rcq-mcard.skel{pointer-events:none}
.rcq-mcard.skel .th{background:var(--sf2);animation:rcq-pulse 1.2s ease-in-out infinite}
.rcq-mcard.skel .meta .n,.rcq-mcard.skel .meta .s{height:9px;background:var(--sf2);border-radius:4px;margin:4px 0}
.rcq-qrow.skel{pointer-events:none}
.rcq-qrow.skel .ava-sk{width:18px;height:18px;border-radius:50%;background:var(--sf2);display:inline-block}
.rcq-qrow.skel .ln-sk{display:block;height:9px;background:var(--sf2);border-radius:4px;margin:5px 0}
.rcq-qrow.skel .w40{width:40%}.rcq-qrow.skel .w80{width:80%}.rcq-qrow.skel .w60{width:60%}
@keyframes rcq-pulse{0%,100%{opacity:.5}50%{opacity:.95}}

/* \u5A92\u4F53\u5E93\u7B5B\u9009\u7F51\u683C / \u66F4\u591A\u83DC\u5355 / \u6279\u91CF\u6761 */
.rcq-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px 14px;align-items:end}
.rcq-grid .rcq-fi{margin:0}
.rcq-grid .rcq-hit{align-self:center}
.rcq-acts{display:flex;gap:8px;justify-content:flex-end;align-items:end}
.rcq-more{position:relative}
.rcq-more-pop{position:absolute;right:0;top:calc(100% + 6px);z-index:8;background:var(--sf);border:1px solid var(--bd);
 border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.22);padding:4px;min-width:160px;display:flex;flex-direction:column}
.rcq-more-pop button{border:none;background:none;text-align:left;padding:7px 10px;border-radius:6px;
 color:var(--t);font-family:inherit;font-size:12px;cursor:pointer}
.rcq-more-pop button:hover{background:var(--sf2)}
.rcq-more-pop button:disabled{opacity:.45;cursor:default}
.rcq-batch{position:sticky;bottom:12px;z-index:7;margin:12px 0 0;display:flex;align-items:center;gap:10px;flex-wrap:wrap;
 background:var(--sf);border:1px solid var(--bd);border-radius:12px;padding:10px 14px;box-shadow:0 8px 24px rgba(0,0,0,.25)}
.rcq-mcard .vid-ic{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
 font-size:26px;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.65);pointer-events:none}
.rcq-badge{display:inline-block;font-size:10px;line-height:1.7;padding:0 6px;border-radius:999px;
 border:1px solid var(--bd);color:var(--m);margin-left:4px;vertical-align:middle}
.rcq-badge.warn{border-color:var(--warn);color:var(--warn)}
.rcq-badge.bad{border-color:var(--bad);color:var(--bad)}
.rcq-badge.plain{border-style:dashed}

/* ---- \u67E5\u8BE2 ---- */
.rcq-qres{display:flex;flex-direction:column;gap:6px}
.rcq-qrow{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:8px 11px}
.rcq-qrow.rec{opacity:.72}
.rcq-qrow .hd{display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:11.5px;color:var(--m)}
.rcq-qrow .hd .ava{width:18px;height:18px;border-radius:50%;object-fit:cover;flex:none}
.rcq-qrow .hd b{font-size:12px;color:var(--t)}
.rcq-qrow .hd .tt{margin-left:auto}
.rcq-qrow .bd{margin-top:5px;font-size:12.5px;white-space:pre-wrap;word-break:break-word;line-height:1.55}
.rcq-sugg{position:absolute;top:100%;left:0;right:0;z-index:50;background:var(--sf);
 border:1px solid var(--bd);border-radius:var(--r);box-shadow:var(--shadow);margin-top:2px;
 max-height:230px;overflow:auto}
.rcq-sugg-i{display:flex;align-items:center;gap:7px;padding:6px 9px;cursor:pointer;font-size:12px}
.rcq-sugg-i:hover{background:var(--sf2)}
.rcq-sugg-i img{width:20px;height:20px;border-radius:50%;object-fit:cover}
.rcq-sugg-i b{font-weight:600}
.rcq-sugg-i span{color:var(--m);font-size:11px}
.rcq-sugg-i i{margin-left:auto;font-style:normal;color:var(--m);font-size:11px}
.rcq-noplay{display:inline-flex;align-items:center;gap:6px;font-size:11.5px;color:var(--warn);
 border:1px solid var(--warn);border-radius:7px;padding:4px 9px;margin-top:5px}
.rcq-noplay a{color:var(--ac)}

/* \u5927\u56FE\u67E5\u770B */
.rcq-light{position:fixed;inset:0;z-index:9998;background:rgba(0,0,0,.82);
 display:flex;align-items:center;justify-content:center;padding:24px;cursor:zoom-out}
.rcq-light img{max-width:100%;max-height:100%;border-radius:8px}
.rcq-light .x{position:absolute;top:16px;right:20px;color:#fff;font-size:24px;
 background:none;border:none;cursor:pointer;line-height:1}

/* \u6C34\u4F4D\u6761 */
.rcq-wl{height:6px;background:var(--sf3);border-radius:3px;overflow:hidden;margin-top:6px}
.rcq-wl i{display:block;height:100%;background:var(--ok);border-radius:3px}
.rcq-wl i.hi{background:var(--warn)}
.rcq-wl i.max{background:var(--bad)}

/* toast */
.rcq-toast{position:fixed;right:24px;bottom:24px;z-index:9999;max-width:420px;
 padding:10px 15px;font-size:12.5px;background:var(--surface-3);color:var(--text);
 border:1px solid var(--border-strong);border-radius:var(--radius-md);box-shadow:var(--shadow)}
.rcq-toast.ok{border-color:var(--success);color:var(--success)}
.rcq-toast.err{border-color:var(--danger);color:var(--danger)}

@media(max-width:1180px){
 .rcq-ov{grid-template-columns:minmax(0,1fr) minmax(0,1.2fr)}
 .rcq-gauges{grid-column:1/-1;flex-direction:row;justify-content:center;gap:12px}
 .rcq-gauge{flex:1;max-width:240px}
}
@media(max-width:820px){
 .rcq-ov{grid-template-columns:1fr}
 .rcq-split{grid-template-columns:1fr}
 .rcq-counters{grid-template-columns:repeat(3,1fr)}
 .rcq-ct:nth-child(4){border-left:0;border-top:1px solid var(--bd)}
 .rcq-ct:nth-child(5){border-top:1px solid var(--bd)}
}

/* ---- \u89D2\u8272\u5361\u7247 ---- */
/* \u5217\u8868\uFF1A\u5361\u7247\u5899 */
.cd-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px;padding:12px}
.cd-card{position:relative;border:1px solid var(--bd);border-radius:12px;overflow:hidden;
  background:var(--sf);cursor:pointer;transition:transform .12s ease,box-shadow .12s ease}
.cd-card:hover{transform:translateY(-2px);box-shadow:var(--shadow)}
.cd-card.on{border-color:var(--ac);box-shadow:0 0 0 1px var(--ac)}
.cdc-cover{position:relative;aspect-ratio:16/10;background:linear-gradient(135deg,var(--sf3),var(--sf2));
  background-size:cover;background-position:center;display:flex;align-items:center;justify-content:center}
.cdc-fallback{font-size:30px;font-weight:600;color:rgba(255,255,255,.92);
  text-shadow:0 2px 8px rgba(0,0,0,.28)}
.cdc-ava{position:absolute;left:10px;bottom:-14px;width:38px;height:38px;border-radius:10px;
  object-fit:cover;border:2px solid var(--sf);background:var(--sf3)}
.cdc-body{padding:18px 10px 10px}
.cdc-name{font-size:13px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cdc-tag{font-size:11px;color:var(--m);margin-top:2px;line-height:1.35;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.7em}
.cdc-badges{margin-top:6px;display:flex;gap:4px;flex-wrap:wrap}
.cd-tag.v{color:var(--f)}

/* \u8BE6\u60C5\uFF1A\u4E00\u5F20\u5B8C\u6574\u7684\u5927\u5361\u7247 */
.cd-hero{position:relative;border:1px solid var(--bd);border-radius:14px;overflow:hidden;
  background:var(--sf);margin:10px 0 14px}
.cdh-cover{position:absolute;left:0;right:0;top:0;height:132px;background-size:cover;
  background-position:center 28%;opacity:.85}
.cdh-cover::after{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(0,0,0,0) 40%,rgba(0,0,0,.30) 100%)}
.cdh-inner{position:relative;display:flex;align-items:center;gap:13px;padding:18px 18px 14px}
.cd-hero.grad .cdh-name{color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.35)}
.cd-hero.grad .cdh-alias{color:rgba(255,255,255,.82)}
.cd-hero.grad .cdh-tag{color:rgba(255,255,255,.92)}
.cd-hero.grad .cdh-ava{background:rgba(255,255,255,.22);color:#fff;
  border:1px solid rgba(255,255,255,.45)}
.cd-hero.grad .cd-tag{color:#fff;border-color:rgba(255,255,255,.55)}
.cd-hero.grad .cdh-inner::before{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(0,0,0,.30),rgba(0,0,0,.05));pointer-events:none}
.cdh-ava{width:58px;height:58px;border-radius:15px;overflow:hidden;background:var(--sf3);
  display:flex;align-items:center;justify-content:center;font-size:23px;font-weight:600;color:var(--f);
  box-shadow:0 4px 14px rgba(0,0,0,.20);flex:none}
.cdh-ava img{width:100%;height:100%;object-fit:cover;display:block}
.cdh-title{flex:1;min-width:0}
.cdh-name{font-size:17px;font-weight:700;letter-spacing:.01em}
.cdh-alias{font-size:11.5px;color:var(--m);margin-top:2px}
.cdh-tag{font-size:12.5px;color:var(--m);margin-top:4px}
.cdh-badges{display:flex;gap:6px;margin-top:7px;flex-wrap:wrap}
.cdh-sections{position:relative;background:var(--sf);border-top:1px solid var(--bd);
  padding:12px 18px 16px;
  display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.cdh-sec{font-size:12.5px;line-height:1.6;min-width:0}
.cdh-sec>b{display:block;font-size:10.5px;color:var(--f);margin-bottom:5px;letter-spacing:.06em}
.cdh-line{margin-bottom:3px}
.cdh-ex{margin-bottom:7px}
.cdh-ex .u{font-size:11.5px;color:var(--m)}
.cdh-ex .a{margin-top:1px}
.cdh-lore{font-size:11.5px;color:var(--m);margin-bottom:6px;line-height:1.5}
.cdh-lore .k{display:inline-block;margin-right:5px;color:var(--ac)}

.cd-tabs{display:flex;gap:4px;margin:10px 0 0;border-bottom:1px solid var(--bd)}
.cd-tabs button{border:none;background:none;padding:7px 12px;font-size:12.5px;color:var(--m);
  cursor:pointer;border-bottom:2px solid transparent;font-family:inherit}
.cd-tabs button.on{border-bottom-color:var(--ac);font-weight:600}
.cd-blk{border:1px solid var(--bd);border-radius:8px;padding:9px 11px;margin-top:10px}
.cd-blk-h{display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:12.5px}
.cd-blk-h .sp{flex:1}
.cd-item{display:flex;gap:6px;align-items:flex-start;margin-bottom:6px}
.cd-item.col{flex-direction:column}
.cd-item .rcq-ta{flex:1;min-height:52px}
.cd-row2{display:flex;gap:6px;align-items:center;width:100%}
.cd-row2 .input{flex:1;min-width:0}
.cd-x{border:none;background:none;color:var(--m);font-size:15px;line-height:1;cursor:pointer;
  padding:2px 5px;border-radius:4px;font-family:inherit}
.cd-x:hover{background:var(--sf3)}
.rcq-ta.tall{min-height:140px}
`;function Rm(){if(document.getElementById(pp))return;let e=document.createElement("style");e.id=pp,e.textContent=Om,document.head.appendChild(e)}var Pm={data(){return{S:yt,ov:null,busy:!1,err:"",timer:null}},computed:{acc(){return this.ov&&this.ov.account||{}},ver(){return this.ov&&this.ov.versions||{}},sysinfo(){return this.ov&&this.ov.sys||{}},cpu(){return this.sysinfo.cpu||{}},mem(){return this.sysinfo.memory||{}},cnt(){return this.ov&&this.ov.counters||{}},botst(){return this.ov&&this.ov.bot||null},vers(){let e=this.ver;return[["\u6846\u67B6\u7248\u672C",e.framework],["QQ \u7248\u672C",e.qq],["OneBot \u7248\u672C",e.webui]]},cpuPct(){let e=parseFloat((this.cpu.usage||{}).system);return isNaN(e)?0:Math.min(100,Math.round(e))},memPct(){let e=parseFloat(this.mem.total),t=parseFloat((this.mem.usage||{}).system);return!e||!t?0:Math.min(100,Math.round(t/e*100))},online(){return!!this.acc.login&&!this.acc.offline}},async mounted(){await this.load(),this.timer=setInterval(()=>this.load(!0),5e3)},beforeUnmount(){this.timer&&clearInterval(this.timer)},methods:{fmtNum:rn,async load(e){e||(this.busy=!0);try{this.ov=await Ue("qqbot.overview"),this.err=(this.ov.errors||[]).join("\uFF1B")}catch(t){this.err=Z(t)}finally{this.busy=!1}},dash(e){return 264-264*e/100},accAvatar(e){if(e.avatar)return e.avatar;let t=String(e&&e.uin||"");return/^\d{5,12}$/.test(t)?"https://q1.qlogo.cn/g?b=qq&nk="+t+"&s=100":""}},template:`
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-ov">
      <div>
        <div class="rcq-pnl flat">
          <div class="rcq-acct">
            <img class="rcq-ava" :src="accAvatar(acc)" alt="" v-if="accAvatar(acc)" />
            <div class="rcq-ava" v-else></div>
            <div style="min-width:0">
              <div class="rcq-nick">
                {{ acc.nick || '\u672A\u767B\u5F55' }}
                <span class="rcq-dot" :class="online ? 'on' : 'off'"></span>
              </div>
              <div class="rcq-uin">{{ acc.uin || '\u2014' }}</div>
            </div>
          </div>
          <div class="rcq-sec">
            <div class="rcq-ph" style="margin-bottom:10px"><b>\u7CFB\u7EDF\u4FE1\u606F</b></div>
            <div class="rcq-kv">
              <template v-for="row in vers" :key="row[0]">
                <div class="k">{{ row[0] }}</div><div class="v">{{ row[1] || '\u2014' }}</div>
              </template>
              <div class="k">\u7CFB\u7EDF\u7248\u672C</div><div class="v">{{ sysinfo.arch || '\u2014' }}</div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div class="rcq-pnl">
          <div class="rcq-ph"><b>CPU</b><span class="sp"></span>
            <span class="rcq-hint">{{ busy ? '\u5237\u65B0\u4E2D\u2026' : '' }}</span></div>
          <div class="rcq-fld full"><span class="k">\u578B\u53F7</span><span class="v">{{ cpu.model || '\u2014' }}</span></div>
          <div class="rcq-row2">
            <div class="rcq-fld"><span class="k">\u5185\u6838\u6570</span><span class="v">{{ cpu.core || '\u2014' }}</span></div>
            <div class="rcq-fld"><span class="k">\u4E3B\u9891</span><span class="v">{{ cpu.speed ? cpu.speed + ' GHz' : '\u2014' }}</span></div>
            <div class="rcq-fld"><span class="k">\u4F7F\u7528\u7387</span><span class="v">{{ (cpu.usage||{}).system || '\u2014' }}%</span></div>
            <div class="rcq-fld"><span class="k">QQ\u4E3B\u7EBF\u7A0B</span><span class="v">{{ (cpu.usage||{}).qq || '\u2014' }}%</span></div>
          </div>
          <div class="rcq-sec">
            <div class="rcq-ph" style="margin-bottom:10px"><b>\u5185\u5B58</b></div>
            <div class="rcq-fld full"><span class="k">\u603B\u91CF</span><span class="v">{{ mem.total ? mem.total + ' MB' : '\u2014' }}</span></div>
            <div class="rcq-row2">
              <div class="rcq-fld"><span class="k">\u4F7F\u7528\u91CF</span><span class="v">{{ (mem.usage||{}).system ? (mem.usage||{}).system + ' MB' : '\u2014' }}</span></div>
              <div class="rcq-fld"><span class="k">QQ\u4E3B\u7EBF\u7A0B</span><span class="v">{{ (mem.usage||{}).qq ? (mem.usage||{}).qq + ' MB' : '\u2014' }}</span></div>
            </div>
          </div>
        </div>
      </div>

      <div class="rcq-gauges">
        <div class="rcq-gauge">
          <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="42" fill="none" stroke="var(--sf3)" stroke-width="9" />
            <circle cx="50" cy="50" r="42" fill="none" stroke="var(--ac)" stroke-width="9"
              stroke-linecap="round" :stroke-dasharray="264" :stroke-dashoffset="dash(cpuPct)"
              transform="rotate(-90 50 50)" />
          </svg>
          <div class="lbl"><b>{{ cpuPct }}%</b><span>CPU \u5360\u7528</span></div>
        </div>
        <div class="rcq-gauge">
          <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="42" fill="none" stroke="var(--sf3)" stroke-width="9" />
            <circle cx="50" cy="50" r="42" fill="none" stroke="var(--ac)" stroke-width="9"
              stroke-linecap="round" :stroke-dasharray="264" :stroke-dashoffset="dash(memPct)"
              transform="rotate(-90 50 50)" />
          </svg>
          <div class="lbl"><b>{{ memPct }}%</b><span>\u5185\u5B58\u5360\u7528</span></div>
        </div>
      </div>
    </div>

    <div class="rcq-counters" style="grid-template-columns:repeat(4,1fr)">
      <div class="rcq-ct"><b>{{ cnt.groups || 0 }}</b><span>\u7FA4\u804A</span></div>
      <div class="rcq-ct"><b>{{ cnt.friends || 0 }}</b><span>\u597D\u53CB</span></div>
      <div class="rcq-ct"><b>{{ cnt.sessions || 0 }}</b><span>\u4F1A\u8BDD</span></div>
      <div class="rcq-ct"><b>{{ cnt.messages || 0 }}</b><span>\u6D88\u606F</span></div>
    </div>

    <div class="rcq-pnl">
      <div class="rcq-ph"><b>RainCough Bot</b><span class="sp"></span>
        <span class="rcq-lamp" v-if="botst"><b :class="botst.onebot && botst.onebot.connected ? 'on' : 'off'"></b>
          {{ botst.onebot && botst.onebot.connected ? '\u5DF2\u8FDE SnowLuma' : '\u672A\u8FDE\u63A5' }}</span>
        <span class="rcq-lamp" v-else><b class="off"></b>rcbot \u672A\u8FD0\u884C</span>
      </div>
      <div class="rcq-row2" style="margin-top:0">
        <div class="rcq-fld"><span class="k">\u63D0\u4F9B\u5546</span><span class="v">{{ (botst && botst.provider) || '\u2014' }}</span></div>
        <div class="rcq-fld"><span class="k">\u6A21\u578B</span><span class="v">{{ (botst && botst.provider_model) || '\u2014' }}</span></div>
        <div class="rcq-fld"><span class="k">\u4F1A\u8BDD</span><span class="v">{{ botst && botst.stats ? botst.stats.sessions : '\u2014' }} \u4E2A / \u6D88\u606F {{ botst && botst.stats ? fmtNum(botst.stats.messages) : '\u2014' }} \u6761</span></div>
        <div class="rcq-fld"><span class="k">\u4E0A\u4E0B\u6587</span><span class="v">{{ (botst && botst.context && botst.context.max_tokens) ? (botst.context.max_tokens + ' tokens \u7A97\u53E3') : '\u2014' }}</span></div>
      </div>
      <div class="rcq-fld" style="margin-top:10px" v-if="botst && botst.last_error">
        <span class="k">\u6700\u8FD1\u9519\u8BEF</span>
        <span class="v rcq-err" :title="botst.last_error">{{ botst.last_error }}</span>
      </div>
    </div>
  </div>`},jm={data(){return{S:yt,acc:null,busy:"",err:"",vncBusy:!1,loginOpen:!1,msg:"",vncErr:"",novncUrl:"",novncPw:""}},computed:{login(){return!!(this.acc&&this.acc.login)},ready(){return!!(this.acc&&this.acc.core_ready)},online(){return!!(this.acc&&(this.acc.online||this.acc.connected))},uin(){return this.acc&&this.acc.uin||""},nick(){return this.acc&&this.acc.nick||""},avatar(){if(this.acc&&this.acc.avatar)return this.acc.avatar;let e=this.uin;return/^\d{5,12}$/.test(e)?"https://q1.qlogo.cn/g?b=qq&nk="+e+"&s=100":""},statusText(){if(!this.acc)return"\u672A\u77E5";if(this.online&&this.ready)return"\u5DF2\u767B\u5F55";if(this.acc.login)return"\u5DF2\u767B\u5F55\uFF08\u521D\u59CB\u5316\u4E2D\uFF09";let e=this.acc.state||"";return e==="failed"?"\u542F\u52A8\u5931\u8D25":e==="inactive"||e==="exited"?"\u5DF2\u505C\u6B62":e==="active"||e==="running"?"\u8FD0\u884C\u4E2D\uFF08\u672A\u767B\u5F55\uFF09":e==="absent"?"\u672A\u90E8\u7F72":e||"\u672A\u77E5"},statusCls(){return this.online&&this.ready?"ok":this.acc&&this.acc.state==="failed"?"off":""}},async mounted(){await this.load(),this.timer=setInterval(()=>this.load(!0),5e3)},beforeUnmount(){this.timer&&clearInterval(this.timer)},methods:{async load(e){e||(this.busy="load");try{this.acc=await Y("qqbot.account.info"),this.err=this.acc&&this.acc.error||"",this.loginOpen&&this.acc&&!this.acc.login&&this.pollStatus(0)}catch(t){this.err=Z(t)}finally{this.busy=""}},buildNovnc(e){if(!e||!e.novnc_path)return"";let t=location.hostname;return(!t||t==="localhost")&&(t="127.0.0.1"),location.protocol+"//"+t+":"+(e.novnc_port||6081)+e.novnc_path},async showLogin(){this.vncBusy=!0,this.vncErr="",this.msg="",this.novncUrl="",this.loginOpen=!0;try{let e=await Y("qqbot.account.qrcode",{});if(e&&e.login){this.msg="\u5DF2\u7ECF\u767B\u5F55\u4E86\uFF1A"+(e.nick||e.uin),await this.load(!0);return}this.novncUrl=this.buildNovnc(e||{}),this.novncPw=e&&e.novnc_password||"",this.novncUrl||(this.vncErr="\u8FDC\u7A0B\u684C\u9762\u5730\u5740\u6CA1\u62FC\u51FA\u6765\uFF08\u7F3A noVNC \u7AEF\u53E3\u6216\u8DEF\u5F84\uFF09"),this.pollStatus(0)}catch(e){this.vncErr=Z(e)}finally{this.vncBusy=!1}},pollStatus(e){e>100||!this.loginOpen||setTimeout(async()=>{if(this.loginOpen){try{let t=await Y("qqbot.account.status",{});if(t&&t.done){this.msg="\u767B\u5F55\u6210\u529F\uFF1A"+(t.nick||t.uin)+"\uFF08"+t.uin+"\uFF09",D("\u5DF2\u767B\u5F55 "+t.uin,"ok"),await this.load(!0),setTimeout(()=>{this.loginOpen=!1},1200);return}t&&t.error?this.msg=t.error:t&&t.phase==="waiting_qrcode"&&(this.msg="\u8BF7\u5728\u8FDC\u7A0B\u684C\u9762\u91CC\u7528\u624B\u673A QQ \u626B\u7801\u2026")}catch(t){this.msg=Z(t)}this.pollStatus(e+1)}},3e3)},async act(e){this.busy=e;try{let t={start:"\u5DF2\u542F\u52A8",stop:"\u5DF2\u505C\u6B62",restart:"\u5DF2\u91CD\u542F",logout:"\u5DF2\u9000\u51FA\u767B\u5F55"}[e]||"\u5DF2\u6267\u884C";if(e==="logout"&&!confirm("\u9000\u51FA\u767B\u5F55\u4F1A\u6E05\u6389\u672C\u673A\u7684\u767B\u5F55\u6001\uFF0C\u4E0B\u6B21\u8981\u91CD\u65B0\u626B\u7801\u3002\u786E\u5B9A\uFF1F"))return;await Ue("qqbot.account.action",{action:e}),D(t,"ok"),this.loginOpen=!1,await this.load(!0)}catch(t){D(Z(t),"err")}finally{this.busy=""}},closeLogin(){this.loginOpen=!1,this.msg="",this.novncUrl="",this.vncErr=""}},template:`
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-pnl">
      <div class="rcq-ph">
        <b>QQ \u8D26\u6237</b>
        <span class="rcq-hint">SnowLuma \xB7 \u5355\u8D26\u6237</span>
        <span class="sp"></span>
        <button class="btn btn-sm btn-primary" :disabled="vncBusy" @click="showLogin()">
          {{ vncBusy ? '\u51C6\u5907\u4E2D\u2026' : (login ? '\u91CD\u65B0\u767B\u5F55' : '\u626B\u7801\u767B\u5F55') }}
        </button>
        <button class="btn btn-sm" :disabled="!!busy" @click="load()">\u5237\u65B0</button>
      </div>

      <div class="rcq-acct" style="padding:16px">
        <img class="rcq-ava" :src="avatar" alt="" v-if="avatar" />
        <div class="rcq-ava" v-else></div>
        <div style="min-width:0;flex:1">
          <div class="rcq-nick">
            {{ nick || (uin ? 'QQ ' + uin : '\u672A\u767B\u5F55') }}
            <span class="rcq-pill" :class="statusCls">{{ statusText }}</span>
          </div>
          <div class="rcq-uin">{{ uin || '\u8FD8\u6CA1\u6709\u767B\u5F55 QQ \u8D26\u53F7' }}</div>
        </div>
      </div>

      <div class="rcq-iacts" style="margin-top:12px">
        <button class="btn btn-sm" :disabled="!!busy" @click="act('start')">\u542F\u52A8</button>
        <button class="btn btn-sm" :disabled="!!busy" @click="act('restart')">\u91CD\u542F</button>
        <button class="btn btn-sm" :disabled="!!busy" @click="act('stop')">\u505C\u6B62</button>
        <button class="btn btn-sm" :disabled="!!busy || !login" @click="act('logout')">\u9000\u51FA\u767B\u5F55</button>
      </div>

      <div v-if="loginOpen" class="rcq-scan">
        <div class="rcq-vncbar">
          <b>\u8FDC\u7A0B\u684C\u9762</b>
          <span class="rcq-hint">\u5728\u4E0B\u9762\u7684\u753B\u9762\u91CC\u7528\u624B\u673A QQ \u626B\u7801\u767B\u5F55</span>
          <span class="sp"></span>
          <a v-if="novncUrl" :href="novncUrl" target="_blank" rel="noopener"
            class="btn btn-sm">\u65B0\u7A97\u53E3\u6253\u5F00</a>
          <button class="btn btn-sm" @click="closeLogin()">\u5173\u95ED</button>
        </div>
        <div v-if="novncUrl" class="rcq-vncwrap">
          <iframe :src="novncUrl" class="rcq-vnc" allow="clipboard-read; clipboard-write"
            referrerpolicy="no-referrer"></iframe>
        </div>
        <div v-else class="rcq-empty2">
          {{ vncErr || (vncBusy ? '\u6B63\u5728\u542F\u52A8\u5BB9\u5668\u4E0E\u8FDC\u7A0B\u684C\u9762\u2026' : '\u8FDC\u7A0B\u684C\u9762\u8FD8\u6CA1\u51C6\u5907\u597D') }}
        </div>
        <div class="rcq-note" style="display:block;margin-top:8px">
          \u753B\u9762\u662F SnowLuma \u5BB9\u5668\u91CC\u7684 QQ \u684C\u9762\uFF0C\u53EF\u4EE5\u76F4\u63A5\u7528\u9F20\u6807\u64CD\u4F5C\u3002
          <br />
          <b>\u5982\u679C\u4E8C\u7EF4\u7801\u663E\u793A\u300C\u5DF2\u8FC7\u671F\u300D\uFF0C\u70B9\u753B\u9762\u91CC\u90A3\u4E2A\u300C\u5237\u65B0\u300D\u6309\u94AE</b>\uFF1B
          \u9996\u6B21\u542F\u52A8\u8981\u7B49 10~30 \u79D2\u5BB9\u5668\u8D77\u6765\u3002
          <br />
          \u5982\u679C\u8FD9\u91CC\u662F\u7A7A\u767D\uFF0C\u8BF4\u660E\u6D4F\u89C8\u5668\u4E0D\u5141\u8BB8\u5185\u5D4C \u2014\u2014 \u70B9\u53F3\u4E0A\u89D2\u300C\u65B0\u7A97\u53E3\u6253\u5F00\u300D\u3002
          <template v-if="novncPw">
            <br />\u8FDC\u7A0B\u684C\u9762\u5BC6\u7801\uFF1A<code>{{ novncPw }}</code>\uFF08\u65B0\u7A97\u53E3\u6253\u5F00\u65F6\u53EF\u80FD\u8981\u8F93\uFF09
          </template>
        </div>
        <div v-if="msg" style="margin-top:8px;font-size:12px">{{ msg }}</div>
      </div>

      <div class="rcq-note" style="margin-top:14px">
        \u672C\u63D2\u4EF6\u662F\u5355\u8D26\u6237\u6A21\u5F0F\uFF1A\u53EA\u7BA1\u7406\u4E00\u4E2A QQ \u53F7\u3002
        <br />
        <b>SnowLuma</b> \u628A QQ \u6574\u5305\u8DD1\u5728 Docker \u91CC\uFF0C\u767B\u5F55\u8981\u5728\u5185\u5D4C\u7684\u8FDC\u7A0B\u684C\u9762\u91CC\u626B\u7801
        \uFF08QQ \u5BA2\u6237\u7AEF\u81EA\u5DF1\u753B\u4E8C\u7EF4\u7801\uFF0C\u6CA1\u6709 API \u80FD\u5355\u72EC\u53D6\u51FA\u6765\uFF09\u3002
        <br />
        \u6362\u53F7\u65F6\u70B9\u300C\u9000\u51FA\u767B\u5F55\u300D\u6E05\u6389\u767B\u5F55\u6001\uFF0C\u518D\u91CD\u65B0\u626B\u7801\u5373\u53EF\u3002
      </div>
    </div>
  </div>`},Lm={components:{ThumbImg:gp},data(){return{S:yt,items:[],stats:null,total:0,kind:"",sender:"",kw:"",sort:"time",moreOpen:!1,limit:60,offset:0,hasMore:!1,busy:"",err:"",light:"",lightKind:"",picked:{},job:null,jobTimer:null}},computed:{kindStats(){let e={};for(let t of(this.stats||{}).items||[])e[t.kind]=t;return e},totalBytes(){return(this.stats||{}).total_bytes||0},totalFiles(){return(this.stats||{}).total_files||0},pickedIds(){return Object.keys(this.picked).filter(e=>this.picked[e]).map(e=>Number(e))},pendingCount(){return this.items.filter(e=>e.transcode==="pending").length},jobPct(){let e=this.job;return!e||!e.total?0:Math.min(100,Math.round(e.done/e.total*100))}},async mounted(){await this.load(),this.$nextTick(()=>this.setupMore())},beforeUnmount(){this._io&&(this._io.disconnect(),this._io=null),this.jobTimer&&(clearInterval(this.jobTimer),this.jobTimer=null)},methods:{fmtFull:mp,fmtNum:rn,mediaAlive:vp,setupMore(){if(typeof IntersectionObserver>"u")return;let e=this.$refs.moreEl;e&&(this._io&&this._io.disconnect(),this._io=new IntersectionObserver(t=>{t.some(i=>i.isIntersecting)&&this.hasMore&&!this.busy&&this.loadMore()},{rootMargin:"300px"}),this._io.observe(e))},bytes(e){return e=Number(e)||0,e>=1073741824?(e/1073741824).toFixed(2)+" G":e>=1048576?(e/1048576).toFixed(1)+" M":e>=1024?(e/1024).toFixed(0)+" K":e+" B"},mediaUrl(e){return fp(e)},kindLabel(e){return{image:"\u56FE\u7247",video:"\u89C6\u9891",record:"\u8BED\u97F3",face:"\u8868\u60C5",file:"\u6587\u4EF6"}[e]||e||"\u5176\u5B83"},kindIcon(e){return{image:"\u{1F5BC}",video:"\u{1F3AC}",record:"\u{1F3A4}",face:"\u{1F600}",file:"\u{1F4CE}"}[e]||"\u{1F4C4}"},async load(e){this.busy="load";try{let t=await Y("qqbot.chat.media_list",{kind:this.kind,sender:this.sender,kw:this.kw,sort:this.sort,limit:this.limit,offset:e?this.offset:0,with_stats:e?0:1}),i=t&&t.items||[];this.items=e?this.items.concat(i):i,this.stats=t&&t.stats||this.stats,this.total=t&&t.total||this.items.length,this.offset=this.items.length,this.hasMore=!!(t&&t.has_more)}catch(t){this.err=Z(t)}finally{this.busy="",this.$nextTick(()=>this.setupMore())}},async reload(){this.offset=0,this.picked={},await this.load(!1)},setKind(e){this.kind=e,this.reload()},clearFilters(){this.kind="",this.sender="",this.kw="",this.reload()},async purgeAll(){if(confirm(`\u6E05\u7406\u5A92\u4F53\u526F\u672C\uFF1F

\u53EA\u5220\u56FE\u7247/\u8BED\u97F3/\u89C6\u9891\u8FD9\u4E9B\u5A92\u4F53\u6587\u4EF6\uFF0C\u804A\u5929\u8BB0\u5F55\u6587\u5B57\u4E00\u6761\u4E0D\u5220\u3002`)){this.busy="purge";try{let e=await Y("qqbot.chat.purge_media",{confirm:!0});D("\u5DF2\u6E05\u7406 "+(e&&e.files||0)+" \u4E2A\u6587\u4EF6\uFF0C\u91CA\u653E "+this.bytes(e&&e.bytes||0),"ok"),await this.reload()}catch(e){D(Z(e),"err")}finally{this.busy=""}}},async loadMore(){await this.load(!0)},toggle(e){this.picked[e]=!this.picked[e]},pickAll(){let e=this.items.every(i=>this.picked[i.id]),t={};if(!e)for(let i of this.items)t[i.id]=!0;this.picked=t},open(e){this.lightKind=e.kind,this.light=this.mediaUrl(e)},async transcode(){let e=this.pickedIds.length?this.pickedIds:null;if(!(!e&&!confirm(`\u628A\u5A92\u4F53\u5E93\u91CC\u6240\u6709\u300C\u6D4F\u89C8\u5668\u653E\u4E0D\u4E86\u300D\u7684\u89C6\u9891/\u8BED\u97F3\u8F6C\u6210\u53EF\u64AD\u653E\u683C\u5F0F\uFF1F

\u8F6C\u6362\u5728\u540E\u53F0\u8FDB\u884C\uFF0C\u53EF\u4EE5\u968F\u65F6\u53D6\u6D88\u3002`))){this.busy="transcode";try{let t=await Y("qqbot.chat.media_transcode",e?{ids:e,async:!0}:{async:!0});t&&t.job?(this.job={id:t.job,state:"running",total:t.total||0,done:0,ok:0,failed:0},this.pollJob()):(D("\u8F6C\u7801\u5B8C\u6210\uFF1A\u6210\u529F "+(t.ok||0)+"\uFF0C\u5931\u8D25 "+(t.failed||0),"ok"),await this.reload())}catch(t){D(Z(t),"err")}finally{this.busy=""}}},pollJob(){this.jobTimer&&clearInterval(this.jobTimer),this.jobTimer=setInterval(async()=>{if(!this.job){clearInterval(this.jobTimer),this.jobTimer=null;return}try{let e=await Y("qqbot.chat.media_task",{id:this.job.id});e&&(this.job=Object.assign({},this.job,e)),this.job.state!=="running"&&(clearInterval(this.jobTimer),this.jobTimer=null,D("\u8F6C\u7801"+(this.job.state==="cancelled"?"\u5DF2\u53D6\u6D88":"\u5B8C\u6210")+"\uFF1A\u6210\u529F "+this.job.ok+"\uFF0C\u5931\u8D25 "+this.job.failed,"ok"),setTimeout(()=>{this.job=null,this.reload()},1200))}catch{}},1200)},async cancelJob(){if(this.job)try{await Y("qqbot.chat.media_task",{id:this.job.id,cancel:!0})}catch{}},async remove(){let e=this.pickedIds;if(!e.length){D("\u5148\u52FE\u9009\u8981\u5220\u9664\u7684\u5A92\u4F53","err");return}if(confirm("\u5220\u9664\u9009\u4E2D\u7684 "+e.length+` \u4E2A\u5A92\u4F53\u6587\u4EF6\uFF1F

\u78C1\u76D8\u4E0A\u7684\u6587\u4EF6\u4F1A\u771F\u7684\u5220\u6389\uFF0C\u804A\u5929\u8BB0\u5F55\u91CC\u7684\u4F4D\u7F6E\u4F1A\u53D8\u6210\u300C\u5DF2\u5931\u6548\u300D\u3002`)){this.busy="del";try{let t=await Y("qqbot.chat.media_delete",{ids:e,confirm:!0});D("\u5DF2\u5220\u9664 "+(t.files||0)+" \u4E2A\u6587\u4EF6\uFF0C\u91CA\u653E "+this.bytes(t.bytes||0),"ok"),await this.reload()}catch(t){D(Z(t),"err")}finally{this.busy=""}}},async reindex(){this.busy="reindex";try{let e=await Y("qqbot.chat.media_reindex",{});D("\u5DF2\u91CD\u5EFA\u7D22\u5F15\uFF1A"+(e.indexed||0)+" \u4E2A\u5A92\u4F53"+(e.cleaned?"\uFF0C\u6E05\u7406\u50F5\u5C38 "+e.cleaned:""),"ok"),await this.reload()}catch(e){D(Z(e),"err")}finally{this.busy=""}},async repair(){this.busy="repair";try{let e=await Y("qqbot.chat.media_repair",{});D("\u5DF2\u4FEE\u590D "+(e.fixed||0)+" \u6761\u6D88\u606F\u7684\u5A92\u4F53\u5F15\u7528","ok"),await this.reload()}catch(e){D(Z(e),"err")}finally{this.busy=""}}},template:`
  <div @click="moreOpen = false">
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-pnl">
      <div class="rcq-flex" style="gap:6px">
        <button class="btn btn-sm" :class="kind === '' ? 'btn-primary' : ''" @click="setKind('')">
          \u5168\u90E8 {{ fmtNum(totalFiles) }} \u4E2A \xB7 {{ bytes(totalBytes) }}</button>
        <button v-for="s in (stats || {}).items || []" :key="s.kind" class="btn btn-sm"
          :class="kind === s.kind ? 'btn-primary' : ''" @click="setKind(s.kind)">
          {{ kindLabel(s.kind) }} {{ fmtNum(s.count) }} \xB7 {{ bytes(s.bytes) }}</button>
        <span style="margin-left:auto"></span>
        <button class="btn btn-sm" :disabled="!!busy" @click="reindex">\u91CD\u5EFA\u7D22\u5F15</button>
        <button class="btn btn-sm" :disabled="!!busy" @click="repair">\u4FEE\u590D\u5F15\u7528</button>
        <button class="btn btn-sm" :disabled="!!busy || !!(job && job.state === 'running')" @click="transcode">
          {{ (job && job.state === 'running') ? ('\u8F6C\u7801\u4E2D ' + job.done + '/' + job.total) : '\u8F6C\u6210\u53EF\u64AD\u653E\u683C\u5F0F' }}
        </button>
        <div class="rcq-more">
          <button class="btn btn-sm" @click.stop="moreOpen = !moreOpen">\u66F4\u591A \u25BE</button>
          <div v-if="moreOpen" class="rcq-more-pop" @click.stop>
            <button :disabled="!pickedIds.length" @click="remove(); moreOpen = false">
              \u5220\u9664\u9009\u4E2D{{ pickedIds.length ? '\uFF08' + pickedIds.length + '\uFF09' : '' }}</button>
            <button @click="purgeAll(); moreOpen = false">\u6E05\u7406\u5A92\u4F53\u526F\u672C</button>
          </div>
        </div>
      </div>
      <div class="rcq-note">
        \u70B9\u51FB\u4E0A\u9762\u7684\u7C7B\u578B\u53EF\u4EE5\u7B5B\u9009\uFF1B\u300C\u8F6C\u6210\u53EF\u64AD\u653E\u683C\u5F0F\u300D\u5728\u540E\u53F0\u8F6C\u7801\uFF0C\u53EF\u968F\u65F6\u53D6\u6D88\u3002
        QQ \u7684\u89C6\u9891\u591A\u662F HEVC\u3001\u8BED\u97F3\u662F AMR\uFF0C\u6D4F\u89C8\u5668\u653E\u4E0D\u4E86 \u2014\u2014 \u8F6C\u5B8C\u53D8\u6210 H.264 / mp3\u3002
      </div>
    </div>

    <div v-if="job" class="rcq-pnl">
      <div class="rcq-flex">
        <b>\u540E\u53F0\u8F6C\u7801 {{ job.done }}/{{ job.total }}</b>
        <span class="rcq-hint">\u6210\u529F {{ job.ok }} \xB7 \u5931\u8D25 {{ job.failed }}</span>
        <span style="margin-left:auto"></span>
        <button v-if="job.state === 'running'" class="btn btn-sm" @click="cancelJob">\u53D6\u6D88</button>
      </div>
      <div class="rcq-bar2" style="margin-top:8px"><i :style="{ width: jobPct + '%' }"></i></div>
    </div>

    <div class="rcq-pnl">
      <div class="rcq-grid">
        <label class="rcq-fi">
          <span>\u53D1\u9001\u8005</span>
          <input class="input" v-model="sender" placeholder="QQ \u53F7\u6216\u6635\u79F0" @keyup.enter="reload()" />
        </label>
        <label class="rcq-fi">
          <span>\u6587\u4EF6\u540D\u5173\u952E\u8BCD</span>
          <input class="input" v-model="kw" placeholder="\u6587\u4EF6\u540D" @keyup.enter="reload()" />
        </label>
        <label class="rcq-fi">
          <span>\u6392\u5E8F</span>
          <select class="input" v-model="sort" @change="reload()">
            <option value="time">\u6309\u65F6\u95F4\uFF08\u65B0\u2192\u65E7\uFF09</option>
            <option value="size">\u6309\u5927\u5C0F\uFF08\u5927\u2192\u5C0F\uFF09</option>
            <option value="kind">\u6309\u7C7B\u578B</option>
          </select>
        </label>
        <div class="rcq-fld rcq-hit"><span class="k">\u547D\u4E2D</span>
          <span class="v">{{ fmtNum(total) }} \u4E2A</span></div>
        <div class="rcq-acts">
          <button class="btn btn-sm btn-primary" :disabled="!!busy" @click="reload">\u7B5B\u9009</button>
          <button class="btn btn-sm" @click="clearFilters">\u6E05\u7A7A</button>
        </div>
      </div>
    </div>

    <div v-if="busy === 'load' && !items.length" class="rcq-mlib">
      <div v-for="i in 12" :key="'sk' + i" class="rcq-mcard skel"><div class="th"></div><div class="meta"><div class="n"></div><div class="s"></div></div></div>
    </div>
    <div v-else-if="!items.length" class="rcq-empty2">\u8FD8\u6CA1\u6709\u5A92\u4F53\u6587\u4EF6</div>
    <div v-else class="rcq-mlib">
      <div v-for="m in items" :key="m.id" class="rcq-mcard"
        :class="{ on: picked[m.id], gone: !m.exists }">
        <label class="ck" @click.stop>
          <input type="checkbox" :checked="!!picked[m.id]" @change="toggle(m.id)" />
        </label>
        <div class="th" @click="m.exists ? open(m) : null">
          <thumb-img v-if="m.exists && (m.kind === 'image' || m.kind === 'face')" :rel="m.rel" :size="360" />
          <!-- preload="metadata"\uFF1A\u53EA\u53D6 moov + \u9996\u5E27\uFF0C\u80FD\u663E\u793A\u7F29\u7565\u56FE\u53C8\u4E0D\u4F1A\u62C9\u6574\u4E2A\u89C6\u9891 -->
          <video v-else-if="m.exists && m.kind === 'video'" :src="mediaUrl(m)" preload="metadata"
            muted playsinline></video>
          <span v-if="m.exists && m.kind === 'video'" class="vid-ic">\u25B6</span>
          <div v-else class="ph">{{ kindIcon(m.kind) }}</div>
          <span v-if="m.transcode === 'pending'" class="rcq-badge warn">\u8F6C\u7801\u4E2D</span>
          <span v-else-if="m.transcode === 'failed'" class="rcq-badge bad">\u683C\u5F0F\u4E0D\u652F\u6301</span>
          <span v-else-if="!m.exists" class="rcq-badge bad">\u5DF2\u4E22\u5931</span>
        </div>
        <div class="meta">
          <div class="n">{{ kindLabel(m.kind) }} \xB7 {{ bytes(m.bytes) }}</div>
          <div class="s">{{ m.sender_name || m.sender_id || '\u672A\u77E5' }}</div>
          <div class="t">{{ fmtFull(m.created_at) }}</div>
        </div>
        <a class="dl" v-if="m.exists" :href="mediaUrl(m)" download>\u4E0B\u8F7D</a>
        <span class="dl gone" v-else>\u6587\u4EF6\u5DF2\u4E22\u5931</span>
      </div>
    </div>
    <div v-if="hasMore" ref="moreEl" class="rcq-loadmore" @click="loadMore()">
      {{ busy ? '\u52A0\u8F7D\u4E2D\u2026' : '\u52A0\u8F7D\u66F4\u591A' }}</div>

    <div v-if="pickedIds.length" class="rcq-batch">
      <b>\u5DF2\u9009 {{ pickedIds.length }} \u9879</b>
      <button class="btn btn-sm" @click="pickAll()">
        {{ pickedIds.length === items.length && items.length ? '\u53D6\u6D88\u5168\u9009' : '\u5168\u9009\u672C\u9875' }}</button>
      <button class="btn btn-sm btn-primary" :disabled="!!busy || !!(job && job.state === 'running')"
        @click="transcode">\u8F6C\u7801\u9009\u4E2D</button>
      <button class="btn btn-sm btn-danger" :disabled="!!busy" @click="remove">\u5220\u9664</button>
      <button class="btn btn-sm" @click="picked = {}">\u53D6\u6D88\u9009\u62E9</button>
    </div>

    <div v-if="light" class="rcq-light" @click="light = ''">
      <button class="x" @click.stop="light = ''">\xD7</button>
      <img v-if="lightKind === 'image' || lightKind === 'face'" :src="light" alt="" />
      <video v-else-if="lightKind === 'video'" :src="light" controls autoplay
        style="max-width:100%;max-height:100%"></video>
      <audio v-else-if="lightKind === 'record'" :src="light" controls autoplay
        style="width:min(520px,90vw)"></audio>
      <a v-else :href="light" download style="color:#fff">\u4E0B\u8F7D\u6587\u4EF6</a>
    </div>
  </div>`},Fm={components:{ThumbImg:gp},data(){return{S:yt,items:[],senders:[],total:0,sender:"",recalled:"",kind:"",kw:"",limit:50,beforeId:0,more:!1,busy:"",err:"",light:"",lightKind:"",lastMs:0,showSenders:!1}},computed:{filtersOn(){return!!(this.sender||this.recalled||this.kind||this.kw)},recalledOpts(){return[{v:"",t:"\u5168\u90E8"},{v:"no",t:"\u672A\u64A4\u56DE"},{v:"yes",t:"\u5DF2\u64A4\u56DE"}]},kindOpts(){return[{v:"",t:"\u5168\u90E8"},{v:"text",t:"\u6587\u672C"},{v:"image",t:"\u56FE\u7247"},{v:"video",t:"\u89C6\u9891"},{v:"record",t:"\u8BED\u97F3"},{v:"face",t:"\u8868\u60C5"},{v:"file",t:"\u6587\u4EF6"}]},suggest(){let e=String(this.sender||"").trim().toLowerCase();return e?this.senders.filter(t=>{let i=String(t.sender_id||""),s=String(t.sender_name||"");return i.indexOf(e)>=0||s.toLowerCase().indexOf(e)>=0}).slice(0,8):[]}},async mounted(){await this.search(!1),this.$nextTick(()=>this.setupMore())},beforeUnmount(){this._io&&(this._io.disconnect(),this._io=null)},methods:{fmtFull:mp,fmtNum:rn,mediaAlive:vp,setupMore(){if(typeof IntersectionObserver>"u")return;let e=this.$refs.moreEl;e&&(this._io&&this._io.disconnect(),this._io=new IntersectionObserver(t=>{t.some(i=>i.isIntersecting)&&this.more&&!this.busy&&this.loadMore()},{rootMargin:"300px"}),this._io.observe(e))},bytes(e){return e=Number(e)||0,e>=1048576?(e/1048576).toFixed(1)+" M":e>=1024?(e/1024).toFixed(0)+" K":e+" B"},mediaUrl(e){return fp(e)},kindLabel(e){return{image:"\u56FE\u7247",video:"\u89C6\u9891",record:"\u8BED\u97F3",face:"\u8868\u60C5",file:"\u6587\u4EF6"}[e]||e||"\u5176\u5B83"},async loadSenders(e){try{let t=await Y("qqbot.chat.senders",{kw:e||"",limit:20});this.senders=t&&t.items||[]}catch{}},onSenderFocus(){this.showSenders=!0,this.loadSenders(this.sender)},onSenderInput(){this.showSenders=!0,clearTimeout(this._st),this._st=setTimeout(()=>this.loadSenders(this.sender),250)},async search(e){this.busy="search";let t=performance.now();try{let i=await Y("qqbot.chat.query",{sender:this.sender,recalled:this.recalled,kind:this.kind,kw:this.kw,limit:this.limit,before_id:e?this.beforeId:0}),s=i&&i.items||[];this.items=e?this.items.concat(s):s,this.total=i&&i.total!==void 0?i.total:this.items.length,this.beforeId=s.length?s[s.length-1].id:0,this.more=!!(i&&i.has_more),this.lastMs=Math.round(performance.now()-t)}catch(i){this.err=Z(i)}finally{this.busy="",this.$nextTick(()=>this.setupMore())}},async reload(){this.beforeId=0,await this.search(!1)},async loadMore(){await this.search(!0)},pickSender(e){this.sender=e.sender_id||e.sender_name||"",this.showSenders=!1,this.reload()},clearFilters(){this.sender="",this.recalled="",this.kind="",this.kw="",this.reload()},openMedia(e){this.lightKind=e.kind,this.light=this.mediaUrl(e)},kindsOf(e){let t=[];for(let i of e.media||[]){let s=i.kind||"";s&&t.indexOf(s)<0&&t.push(s)}return t}},template:`
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-pnl">
      <div class="rcq-grid">
        <label class="rcq-fi" style="position:relative">
          <span>QQ \u7528\u6237</span>
          <input class="input" v-model="sender" placeholder="QQ \u53F7\u6216\u6635\u79F0"
            @focus="onSenderFocus" @input="onSenderInput" @keyup.enter="reload()" />
          <div v-if="showSenders && suggest.length" class="rcq-sugg">
            <div v-for="x in suggest" :key="x.sender_id" class="rcq-sugg-i"
              @click="pickSender(x)">
              <img v-if="x.avatar" :src="x.avatar" alt="" />
              <b>{{ x.sender_name || x.sender_id }}</b>
              <span>{{ x.sender_id }}</span>
              <i>{{ x.c }} \u6761</i>
            </div>
          </div>
        </label>

        <label class="rcq-fi" style="margin:0">
          <span>\u64A4\u56DE\u72B6\u6001</span>
          <select class="input" v-model="recalled" @change="reload()">
            <option v-for="o in recalledOpts" :key="o.v" :value="o.v">{{ o.t }}</option>
          </select>
        </label>

        <label class="rcq-fi" style="margin:0">
          <span>\u6D88\u606F\u7C7B\u578B</span>
          <select class="input" v-model="kind" @change="reload()">
            <option v-for="o in kindOpts" :key="o.v" :value="o.v">{{ o.t }}</option>
          </select>
        </label>

        <label class="rcq-fi" style="margin:0">
          <span>\u5173\u952E\u8BCD</span>
          <input class="input" v-model="kw" placeholder="\u6D88\u606F\u5185\u5BB9" @keyup.enter="reload()" />
        </label>

        <div class="rcq-acts">
          <button class="btn btn-sm" :disabled="!filtersOn" @click="clearFilters">\u6E05\u7A7A\u6761\u4EF6</button>
          <button class="btn btn-sm btn-primary" :disabled="!!busy" @click="reload">
            {{ busy === 'search' ? '\u67E5\u8BE2\u4E2D\u2026' : '\u67E5\u8BE2' }}
          </button>
        </div>
      </div>
      <div class="rcq-note">
        \u5404\u4E2A\u6761\u4EF6\u53EF\u4EE5\u53E0\u52A0\u4F7F\u7528 \u2014\u2014 \u6BD4\u5982\u300C\u67E5\u67D0\u4E2A QQ \u53F7\u7684\u3001\u5DF2\u64A4\u56DE\u7684\u89C6\u9891\u300D\u3002
        \u64A4\u56DE\u72B6\u6001\u3001\u6D88\u606F\u7C7B\u578B\u3001QQ \u7528\u6237\u3001\u5173\u952E\u8BCD\u662F\u300C\u4E0E\u300D\u7684\u5173\u7CFB\u3002
      </div>
    </div>

    <div class="rcq-pnl" v-if="items.length || total">
      <div class="rcq-flex">
        <b>\u547D\u4E2D {{ fmtNum(total) }} \u6761</b>
        <span class="rcq-hint" v-if="lastMs">\u8017\u65F6 {{ lastMs }}ms</span>
        <span style="margin-left:auto"></span>
        <span class="rcq-hint">\u5DF2\u52A0\u8F7D {{ items.length }} \u6761</span>
      </div>
    </div>

    <div v-if="busy === 'search' && !items.length" class="rcq-qres">
      <div v-for="i in 6" :key="'qsk' + i" class="rcq-qrow skel">
        <div class="hd"><span class="ava-sk"></span><span class="ln-sk w40"></span></div>
        <div class="bd"><span class="ln-sk w80"></span><span class="ln-sk w60"></span></div>
      </div>
    </div>
    <div v-else-if="!items.length" class="rcq-empty2">
      \u6CA1\u6709\u7B26\u5408\u6761\u4EF6\u7684\u6D88\u606F
    </div>

    <div class="rcq-qres">
      <div v-for="m in items" :key="m.id" class="rcq-qrow"
        :class="{ rec: m.recalled }">
        <div class="hd">
          <img v-if="m.sender_avatar || m.sender_id" class="ava" loading="lazy"
            :src="m.sender_avatar || ('https://q1.qlogo.cn/g?b=qq&nk=' + m.sender_id + '&s=100')"
            alt="" />
          <b>{{ m.sender_name || m.sender_id }}</b>
          <span class="tt">{{ fmtFull(m.created_at) }}</span>
          <span class="rcq-badge" v-if="m.recalled">\u5DF2\u64A4\u56DE</span>
          <span class="rcq-badge" v-for="k in kindsOf(m)" :key="k">{{ kindLabel(k) }}</span>
          <span class="rcq-badge plain" v-if="m.kind === 'group'">\u7FA4 {{ m.target_id }}</span>
          <span class="rcq-badge plain" v-else>\u79C1\u804A {{ m.target_id }}</span>
        </div>
        <div class="bd">
          <span v-if="m.text && m.text !== '[\u4E00\u6761\u6D88\u606F\u88AB\u64A4\u56DE]'">{{ m.text }}</span>
          <span v-else-if="m.text" style="color:var(--f);font-style:italic">{{ m.text }}</span>
          <div class="rcq-media">
            <template v-for="md in (m.media || [])" :key="md.seg">
              <thumb-img v-if="md.kind === 'image' && mediaAlive(md)" :rel="md.rel" :size="320"
                @click="openMedia(md)" style="max-width:150px;max-height:150px;cursor:zoom-in" />
              <thumb-img v-else-if="md.kind === 'face' && mediaAlive(md)" :rel="md.rel" :size="64"
                style="width:26px;height:26px" />
              <video v-else-if="md.kind === 'video' && mediaAlive(md)" controls preload="metadata"
                :src="mediaUrl(md)" style="max-width:240px"></video>
              <audio v-else-if="md.kind === 'record' && mediaAlive(md)" controls
                :src="mediaUrl(md)" style="max-width:240px"></audio>
              <a v-else-if="md.local && md.exists !== 0" class="rcq-file"
                :href="mediaUrl(md)" download>
                {{ md.name || (md.kind + ' \u6587\u4EF6') }}
              </a>
              <span v-else class="rcq-note">[{{ md.kind }} \u5DF2\u5931\u6548]</span>
            </template>
          </div>
        </div>
      </div>
    </div>
    <div v-if="more" ref="moreEl" class="rcq-loadmore" @click="loadMore()">
      {{ busy ? '\u52A0\u8F7D\u4E2D\u2026' : '\u52A0\u8F7D\u66F4\u591A' }}</div>

    <div v-if="light" class="rcq-light" @click="light = ''">
      <button class="x" @click.stop="light = ''">\xD7</button>
      <img v-if="lightKind === 'image' || lightKind === 'face'" :src="light" alt="" />
      <video v-else-if="lightKind === 'video'" :src="light" controls autoplay
        style="max-width:100%;max-height:100%"></video>
      <audio v-else-if="lightKind === 'record'" :src="light" controls autoplay
        style="width:min(520px,90vw)"></audio>
      <a v-else :href="light" download style="color:#fff">\u4E0B\u8F7D\u6587\u4EF6</a>
    </div>
  </div>`},zm={data(){return{S:yt,list:[],def:"",cur:null,busy:"",err:"",dirty:!1,section:"memory",providers:[],mem:null,memLoading:!1,memSel:null,memDrag:null,memMoved:!1,memoryOpen:!1,showJunk:!1,memQuery:"",memHits:[],memTimer:null,memTiles:{},memExtra:[],tileTimer:null,memStats:null,showStats:!1,hitIndex:0,memScopeKey:"global",memScopes:{groups:[],privates:[]},showKeywords:!1,kwList:[],kwQuery:"",kwLimit:80,kwNew:{match:"",reply:"",mode:"contains",require_at:!0},memView:{s:.8,ox:0,oy:0}}},computed:{isNew(){return!!(this.cur&&this.cur.__new)},themeColor(){return this.cur&&this.cur.style&&this.cur.style.color||""},provName(e){let t=this.providers.find(i=>i.id===e);return t?t.name||t.id:e||"\uFF08\u8DDF\u968F\u8D26\u53F7\u9ED8\u8BA4\uFF09"}},async mounted(){await this.load(),this.loadScopes();try{let e=await Y("rcbot.providers");this.providers=e&&e.items||[]}catch{}},methods:{fmtNum:rn,cloneDeep(e){return JSON.parse(JSON.stringify(e||{}))},grad(e){let t=String(e||""),i=0;for(let s=0;s<t.length;s++)i=(i*31+t.charCodeAt(s))%360;return"linear-gradient(135deg, hsl("+i+" 58% 56%), hsl("+(i+46)%360+" 52% 42%))"},coverStyle(e){let t=e&&e.cover_url||(/^https?:/i.test(e&&e.cover||"")?e.cover:"");return t?{backgroundImage:"url("+t+")"}:{backgroundImage:this.grad((e||{}).name)}},avatarSrc(e){return e?e.avatar_url||(/^https?:/i.test(e.avatar||"")?e.avatar:""):""},assetSrc(e,t){return e&&(e[t+"_url"]||e[t])||""},async load(){this.busy="load";try{let e=await Y("rcbot.cards");if(this.list=e&&e.items||[],this.def=e&&e.default||"",!this.cur||this.cur.__new)this.cur=null,this.memoryOpen=!1;else{let t=this.list.find(i=>i.id===this.cur.id);t&&!this.dirty&&(this.cur=this.cloneDeep(t))}}catch(e){this.err=Z(e)}finally{this.busy=""}},pick(e){this.cur=e?this.cloneDeep(e):null,this.dirty=!1,this.memSel=null,this.memoryOpen=!!this.cur,this.section="memory",this.memQuery="",this.memHits=[],this.memTiles={},this.memExtra=[],this.cur&&this.cur.id&&this.$nextTick(()=>this.loadMemory())},backToList(){this.memoryOpen=!1,this.memSel=null},add(){this.cur={schema:2,id:"",version:1,status:"draft",name:"\u65B0\u89D2\u8272",alias:[],tagline:"",avatar:"",cover:"",portrait:"",prompt:"",taboos:[],keywords:[],style:{temperature:.8,max_tokens:512,max_chars:0,allow_emoji:!1,color:""},model:{provider_id:"",model:""},context:{keep_rounds:20},__new:!0},this.dirty=!0},addGreeting(){this.cur&&(this.cur.greetings=this.cur.greetings||[],this.cur.greetings.push(""))},rmGreeting(e){this.cur&&this.cur.greetings&&this.cur.greetings.splice(e,1)},addExample(){this.cur&&(this.cur.examples=this.cur.examples||[],this.cur.examples.push({user:"",assistant:""}))},rmExample(e){this.cur&&this.cur.examples&&this.cur.examples.splice(e,1)},addLore(){this.cur&&(this.cur.lorebook=this.cur.lorebook||[],this.cur.lorebook.push({keys:[],content:""}))},rmLore(e){this.cur&&this.cur.lorebook&&this.cur.lorebook.splice(e,1)},loreKeys(e){return(e.keys||[]).join("\u3001")},setLoreKeys(e,t){e.keys=String(t||"").split(/[、,，\s]+/).filter(Boolean)},addKw(){this.cur&&(this.cur.keywords=this.cur.keywords||[],this.cur.keywords.push({match:"",reply:"",mode:"contains",require_at:!0,enabled:!0}),this.dirty=!0)},rmKw(e){!this.cur||!this.cur.keywords||(this.cur.keywords.splice(e,1),this.dirty=!0)},taboosText(){return(this.cur&&this.cur.taboos||[]).join(`
`)},setTaboosText(e){this.cur&&(this.cur.taboos=String(e||"").split(`
`).map(t=>t.trim()).filter(Boolean))},memColor(e){return{profile:"#e8c46a",appearance:"#5fd0d8",persona:"#b48cf0",taboo:"#f08c8c",canon:"#7aa8f0",fact:"#6fd08a",event:"#f0a45f",greeting:"#f0d06a",example:"#f08cc8",trigger:"#e05a5a",style:"#8a9ab0",model:"#8a9ab0"}[e]||"#9ab6d0"},memName(e){return{profile:"\u8EAB\u4EFD",appearance:"\u5F62\u8C61",persona:"\u884C\u4E3A",taboo:"\u7981\u5219",canon:"\u8BBE\u5B9A",fact:"\u4E8B\u5B9E",event:"\u4E8B\u4EF6",greeting:"\u5F00\u573A\u767D",example:"\u793A\u4F8B",trigger:"\u89E6\u53D1",style:"\u98CE\u683C",model:"\u6A21\u578B"}[e]||"\u8BB0\u5FC6"},memState(e){return e==="junk"?"\u5783\u573E\u573A":e==="dormant"?"\u4F11\u7720":"\u6B63\u5E38"},openSection(e){this.section=e,e==="memory"&&this.$nextTick(()=>this.loadMemory())},scopeParams(){if(!this.memScopeKey||this.memScopeKey==="global")return{scope_type:"global",scope_id:""};let e=this.memScopeKey.indexOf(":");return{scope_type:this.memScopeKey.slice(0,e),scope_id:this.memScopeKey.slice(e+1)}},async loadScopes(){try{let e=await Y("rcbot.sessions"),t=e&&(e.items||e)||[],i=[],s=[],n={};for(let r of t){let a=r&&(r.target_id||r.target);if(!a||r.kind!=="group"&&r.kind!=="private")continue;let l=r.kind+":"+a;if(n[l])continue;n[l]=1;let o=r.display||r.title||r.name||String(a);r.kind==="group"?i.push({key:l,label:o}):s.push({key:l,label:o})}this.memScopes={groups:i,privates:s}}catch{}},changeScope(){this.memSel=null,this.memHits=[],this.memExtra=[],this.loadMemory()},async loadMemory(){if(!(!this.cur||!this.cur.id)){this.memLoading=!0,this.memTiles={},this.memExtra=[];try{let e=this.scopeParams(),t=await Y("rcbot.memory.map",{card_id:this.cur.id,...e});this.mem=t||null,this.$nextTick(()=>{this.fitMem(),this.ensureTiles()})}catch(e){D(Z(e),"err")}finally{this.memLoading=!1}}},allStars(){let e=[];for(let t in this.memTiles)e.push(...this.memTiles[t]||[]);return e.push(...this.memExtra||[]),e},scheduleTiles(){clearTimeout(this.tileTimer),this.tileTimer=setTimeout(()=>this.ensureTiles(),180)},async ensureTiles(){let e=this.$refs.memCanvas;if(!e||!this.cur||!this.mem)return;let t=e.clientWidth||800,i=e.clientHeight||520,s=this.memView,n=(0-s.ox)/s.s,r=(t-s.ox)/s.s,a=(0-s.oy)/s.s,l=(i-s.oy)/s.s,o=Math.floor(n/512),c=Math.floor(r/512),d=Math.floor(a/512),p=Math.floor(l/512),f=[];for(let y=o;y<=c&&f.length<6;y++)for(let m=d;m<=p&&f.length<6;m++){let x=y+","+m;this.memTiles[x]===void 0&&(this.memTiles[x]=[],f.push(Y("rcbot.memory.tile",{card_id:this.cur.id,tx:y,ty:m,...this.scopeParams()}).then(q=>{this.memTiles[x]=q&&q.items||[]}).catch(()=>{this.memTiles[x]=[]})))}f.length&&(await Promise.all(f),this.drawMem())},fitMem(){let e=this.$refs.memCanvas;if(!e||!this.mem)return;let t=(this.mem.main||[]).concat(this.allStars());if(!t.length)return;let i,s,n,r;if(this.mem.bbox)i=this.mem.bbox.minx,s=this.mem.bbox.maxx,n=this.mem.bbox.miny,r=this.mem.bbox.maxy;else{let c=t.map(p=>p.x),d=t.map(p=>p.y);i=Math.min(...c),s=Math.max(...c),n=Math.min(...d),r=Math.max(...d)}let a=e.clientWidth||800,l=e.clientHeight||520,o=Math.min(a/(s-i+140),l/(r-n+140),2.4);this.memView={s:o,ox:a/2-(i+s)/2*o,oy:l/2-(n+r)/2*o},this.drawMem()},drawMem(){let e=this.$refs.memCanvas;if(!e)return;let t=window.devicePixelRatio||1,i=e.clientWidth||800,s=e.clientHeight||520;(e.width!==Math.round(i*t)||e.height!==Math.round(s*t))&&(e.width=Math.round(i*t),e.height=Math.round(s*t));let n=e.getContext("2d");n.setTransform(t,0,0,t,0,0),n.clearRect(0,0,i,s);let r=n.createRadialGradient(i*.5,s*.42,10,i*.5,s*.42,Math.max(i,s)*.85);r.addColorStop(0,"#101c31"),r.addColorStop(.55,"#0a1220"),r.addColorStop(1,"#04060b"),n.fillStyle=r,n.fillRect(0,0,i,s);let a=(b,u,h,g)=>{let _=n.createRadialGradient(b,u,0,b,u,h);_.addColorStop(0,g),_.addColorStop(1,"rgba(0,0,0,0)"),n.fillStyle=_,n.fillRect(0,0,i,s)};a(i*.18,s*.22,Math.max(i,s)*.62,"rgba(46,96,158,.20)"),a(i*.84,s*.72,Math.max(i,s)*.58,"rgba(112,70,156,.16)"),a(i*.58,s*.1,Math.max(i,s)*.45,"rgba(28,120,136,.12)");for(let b=0;b<140;b++){let u=Math.sin(b*12.9898)*43758.5453%1,h=Math.sin(b*78.233)*12345.6789%1,g=Math.abs(u)*i,_=Math.abs(h)*s;n.fillStyle="rgba(190,214,245,"+(.05+b%5*.012)+")",n.fillRect(g,_,1,1)}let l=n.createRadialGradient(i*.5,s*.5,Math.min(i,s)*.25,i*.5,s*.5,Math.max(i,s)*.72);if(l.addColorStop(0,"rgba(0,0,0,0)"),l.addColorStop(1,"rgba(0,0,0,.52)"),n.fillStyle=l,n.fillRect(0,0,i,s),!this.mem)return;let o=this.memView,c=b=>[b.x*o.s+o.ox,b.y*o.s+o.oy],d={};for(let b of this.mem.main||[])d[b.id]=b;let p={};for(let b of this.mem.clusters||[])p[b.name]=b.count;n.lineWidth=.7;for(let b of this.allStars()){let u=d[b.parent];if(!u)continue;let[h,g]=c(u),[_,k]=c(b);n.strokeStyle="rgba(120,160,220,"+(.1+.25*(b.b||.3))+")",n.beginPath(),n.moveTo(h,g),n.lineTo(_,k),n.stroke()}let f=(b,u,h,g,_)=>{n.beginPath();for(let k=0;k<_*2;k++){let S=k%2?g:h,C=-Math.PI/2+k*Math.PI/_,E=b+Math.cos(C)*S,O=u+Math.sin(C)*S;k?n.lineTo(E,O):n.moveTo(E,O)}n.closePath()},y=new Set((this.memHits||[]).map(b=>b.id)),m=!!(this.memQuery||"").trim()&&y.size>0,x=b=>m&&!y.has(b.id)?.15:1,q=b=>{let[u,h]=c(b);if(u<-30||h<-30||u>i+30||h>s+30)return;let g=Math.max(.08,b.b||.3),_=this.memColor(b.type);if(b.main){let k=14+8*g;n.shadowColor=_,n.shadowBlur=26*g+10,n.fillStyle=_,n.globalAlpha=(.6+.4*g)*x(b),f(u,h,k,k*.4,5),n.fill(),n.shadowBlur=0,n.globalAlpha=.5*g,n.strokeStyle=_,n.lineWidth=1.4,n.beginPath(),n.moveTo(u-k*2.4,h),n.lineTo(u+k*2.4,h),n.moveTo(u,h-k*2.4),n.lineTo(u,h+k*2.4),n.stroke(),n.globalAlpha=.98,n.fillStyle="#ffffff",n.beginPath(),n.arc(u,h,Math.max(1.8,k*.2),0,Math.PI*2),n.fill(),n.globalAlpha=.92,n.fillStyle="rgba(235,244,255,.92)",n.font="13px system-ui, sans-serif",n.fillText(this.memName(b.type)+" \xB7 "+(p[b.type]||""),u+k+8,h+4)}else{let k=2.8+5*g;n.shadowColor=_,n.shadowBlur=10*g+3,n.fillStyle=_,n.globalAlpha=(.32+.68*g)*x(b),f(u,h,k,k*.26,4),n.fill(),n.globalAlpha=.6*g,n.fillStyle="#ffffff",n.beginPath(),n.arc(u,h,Math.max(.8,k*.18),0,Math.PI*2),n.fill()}n.shadowBlur=0,n.globalAlpha=1};for(let b of this.allStars())this.memView.s<.28&&(b.b||.3)<.55&&!m||this.memView.s<.16&&!m||q(b);if(this.showJunk){n.shadowBlur=0;let b=this.mem.junk_stars||[];n.globalAlpha=.55,n.fillStyle="rgba(170,188,210,.8)",n.font="12px system-ui, sans-serif",n.fillText("\u5783\u573E\u573A \xB7 "+b.length,52,s-58);for(let u=0;u<b.length;u++){let h=56+u%20*16,g=s-38+Math.floor(u/20)*16;n.globalAlpha=.22,n.fillStyle="rgba(160,178,200,1)",f(h,g,2,.7,4),n.fill()}n.globalAlpha=1}for(let b of this.mem.main||[])q(b);if(m){n.shadowBlur=0,n.strokeStyle="rgba(255,220,140,.9)",n.lineWidth=1.2;for(let b of this.memHits||[]){let[u,h]=c(b);u<-20||h<-20||u>i+20||h>s+20||(n.beginPath(),n.arc(u,h,13,0,Math.PI*2),n.stroke())}}n.globalAlpha=1},toggleJunk(){this.$nextTick(()=>{this.fitMem(),this.drawMem()})},searchMem(){clearTimeout(this.memTimer),this.memTimer=setTimeout(async()=>{let e=this.memQuery.trim();if(this.cur){if(!e){this.memHits=[],this.drawMem();return}try{let t=await Y("rcbot.memory.search",{card_id:this.cur.id,q:e,...this.scopeParams()});this.memHits=t&&t.items||[],this.hitIndex=0,this.memExtra=this.memHits.slice(),this.memHits.length?this.focusHits():this.drawMem()}catch{}}},260)},async consolidateMem(){if(this.cur&&confirm("\u5408\u5E76\u8FD1\u4F3C\u91CD\u590D\u7684\u8BB0\u5FC6\uFF0C\u5E76\u5F52\u6863\u9648\u65E7\u4E8B\u4EF6\uFF1F"))try{let e=await Y("rcbot.memory.consolidate",{card_id:this.cur.id});D("\u8BB0\u5FC6\u5DF2\u5DE9\u56FA\uFF1A\u5408\u5E76 "+(e&&e.merged||0)+" \u6761\uFF0C\u5F52\u6863 "+(e&&e.stale||0)+" \u6761","ok"),await this.loadMemory(),this.showStats&&(this.memStats=await Y("rcbot.memory.stats",{card_id:this.cur.id}))}catch(e){D(Z(e),"err")}},async openKeywords(){this.showKeywords=!0,this.kwLimit=80,await this.loadKeywords()},async loadKeywords(){if(this.cur)try{let e=await Y("rcbot.memory.triggers",{card_id:this.cur.id});this.kwList=e&&e.items||[]}catch(e){D(Z(e),"err")}},kwFiltered(){let e=(this.kwQuery||"").trim().toLowerCase();return e?this.kwList.filter(t=>(t.match||"").toLowerCase().includes(e)||(t.reply||"").toLowerCase().includes(e)):this.kwList},async saveKw(e){if(!e||!e.match||!e.reply){D("\u5173\u952E\u8BCD\u548C\u56DE\u590D\u90FD\u4E0D\u80FD\u4E3A\u7A7A","err");return}try{await Y("rcbot.memory.save",{item:{id:e.id,card_id:this.cur.id,type:"trigger",mode:"config",content:e.reply,importance:.4,meta:{match:e.match,reply:e.reply,mode:"contains",require_at:!!e.require_at,enabled:e.enabled!==!1}}}),e.enabled=e.enabled!==!1,D("\u5DF2\u4FDD\u5B58\uFF1A"+e.match,"ok")}catch(t){D(Z(t),"err")}},async delKw(e){if(!(!e||!confirm("\u5220\u9664\u5173\u952E\u8BCD\u300C"+e.match+"\u300D\uFF1F")))try{await Y("rcbot.memory.delete",{id:e.id}),this.kwList=this.kwList.filter(t=>t.id!==e.id),D("\u5DF2\u5220\u9664","ok")}catch(t){D(Z(t),"err")}},async addKeyword(){let e=this.kwNew;if(!e.match.trim()||!e.reply.trim()){D("\u5173\u952E\u8BCD\u548C\u56DE\u590D\u90FD\u8981\u586B","err");return}try{await Y("rcbot.memory.save",{item:{card_id:this.cur.id,type:"trigger",mode:"config",content:e.reply.trim(),importance:.4,meta:{match:e.match.trim(),reply:e.reply.trim(),mode:"contains",require_at:!!e.require_at,enabled:!0}}}),e.match="",e.reply="",await this.loadKeywords(),D("\u5DF2\u6DFB\u52A0","ok")}catch(t){D(Z(t),"err")}},async bulkKw(e){let t=this.kwFiltered();if(t.length&&confirm((e?"\u542F\u7528":"\u505C\u7528")+"\u5F53\u524D\u7B5B\u9009\u7684 "+t.length+" \u6761\uFF1F")){for(let i of t)i.enabled=e,await Y("rcbot.memory.save",{item:{id:i.id,card_id:this.cur.id,type:"trigger",mode:"config",content:i.reply,importance:.4,meta:{match:i.match,reply:i.reply,mode:i.mode,require_at:!!i.require_at,enabled:e}}});D("\u5DF2\u66F4\u65B0 "+t.length+" \u6761","ok")}},async toggleStats(){if(this.cur&&(this.showStats=!this.showStats,this.showStats))try{this.memStats=await Y("rcbot.memory.stats",{card_id:this.cur.id})}catch{}},centerOn(e){let t=this.$refs.memCanvas;if(!t)return;let i=t.clientWidth||800,s=t.clientHeight||520,n=Math.max(.8,this.memView.s);this.memView={s:n,ox:i/2-e.x*n,oy:s/2-e.y*n},this.drawMem()},async openHit(e){if(!this.memHits.length)return;let t=this.memHits.length;this.hitIndex=(this.hitIndex+e+t)%t;let i=this.memHits[this.hitIndex];this.centerOn(i);try{this.memSel=await Y("rcbot.memory.item",{id:i.id})}catch{}},async openFirstHit(){if(this.memHits.length)try{this.memSel=await Y("rcbot.memory.item",{id:this.memHits[0].id})}catch{}},clearSearch(){this.memQuery="",this.memHits=[],this.memExtra=[],this.$nextTick(()=>this.fitMem())},focusHits(){let e=this.$refs.memCanvas;if(!e||!this.memHits.length)return;let t=this.memHits.map(d=>d.x),i=this.memHits.map(d=>d.y),s=Math.min(...t),n=Math.max(...t),r=Math.min(...i),a=Math.max(...i),l=e.clientWidth||800,o=e.clientHeight||520,c=Math.min(l/(n-s+220),o/(a-r+220),2.2);this.memView={s:c,ox:l/2-(s+n)/2*c,oy:o/2-(r+a)/2*c},this.drawMem()},memDown(e){this.memDrag={x:e.clientX,y:e.clientY,ox:this.memView.ox,oy:this.memView.oy},this.memMoved=!1},memMove(e){if(!this.memDrag)return;let t=e.clientX-this.memDrag.x,i=e.clientY-this.memDrag.y;Math.abs(t)+Math.abs(i)>3&&(this.memMoved=!0),this.memView={s:this.memView.s,ox:this.memDrag.ox+t,oy:this.memDrag.oy+i},this.drawMem()},memUp(){this.memDrag=null,this.scheduleTiles()},memWheel(e){e.preventDefault();let t=this.$refs.memCanvas;if(!t)return;let i=t.getBoundingClientRect(),s=e.clientX-i.left,n=e.clientY-i.top,r=e.deltaY<0?1.12:.89,a=Math.min(4,Math.max(.15,this.memView.s*r)),l=this.memView;this.memView={s:a,ox:s-(s-l.ox)*(a/l.s),oy:n-(n-l.oy)*(a/l.s)},this.drawMem(),this.scheduleTiles()},async memClick(e){if(this.memMoved){this.memMoved=!1;return}if(!this.mem)return;let t=this.$refs.memCanvas,i=t.getBoundingClientRect(),s=e.clientX-i.left,n=e.clientY-i.top,r=null,a=14,l=(this.mem.main||[]).concat(this.allStars(),this.showJunk?this.mem.junk_stars||[]:[]);for(let o of l){let c=o.x*this.memView.s+this.memView.ox,d=o.y*this.memView.s+this.memView.oy,p=Math.hypot(c-s,d-n);p<a&&(a=p,r=o)}if(!r){if(this.showJunk){let o=t.clientHeight||520;if(n>o-80&&n<o-12&&s>44){let c=Math.floor((s-56)/16),d=Math.floor((n-(o-42))/16);if(c>=0&&c<20&&d>=0){let p=(this.mem.junk_stars||[])[d*20+c];if(p){try{this.memSel=await Y("rcbot.memory.item",{id:p.id})}catch{}return}}}}return}try{this.memSel=await Y("rcbot.memory.item",{id:r.id})}catch(o){D(Z(o),"err")}},async saveMem(){if(this.memSel)try{await Y("rcbot.memory.save",{item:this.memSel}),D("\u8BB0\u5FC6\u5DF2\u4FDD\u5B58","ok");let e=this.memSel.id;this.memSel=await Y("rcbot.memory.item",{id:e}),this.loadMemory()}catch(e){D(Z(e),"err")}},async pinMem(){if(this.memSel)try{await Y("rcbot.memory.pin",{id:this.memSel.id,pinned:!this.memSel.pinned}),this.memSel.pinned=this.memSel.pinned?0:1,this.loadMemory()}catch(e){D(Z(e),"err")}},async delMem(){if(this.memSel&&confirm("\u628A\u8FD9\u6761\u8BB0\u5FC6\u79FB\u5165\u5783\u573E\u573A\uFF1F"))try{await Y("rcbot.memory.delete",{id:this.memSel.id}),this.memSel=null,this.loadMemory()}catch(e){D(Z(e),"err")}},async save(){if(!this.cur)return;let e=this.cloneDeep(this.cur);if(!String(e.name||"").trim()){D("\u89D2\u8272\u540D\u5B57\u4E0D\u80FD\u4E3A\u7A7A","err");return}delete e.__new,this.busy="save";try{let t=await Y("rcbot.card.save",{card:e});D("\u5DF2\u4FDD\u5B58","ok"),this.dirty=!1,this.cur=null,await this.load(),t&&t.id&&this.pick(this.list.find(i=>i.id===t.id)||null)}catch(t){D(Z(t),"err")}finally{this.busy=""}},async setDefault(e){this.busy="def"+e.id;try{let t=this.cloneDeep(e);t.status="published",await Y("rcbot.card.save",{card:t,set_default:!0}),D("\u5DF2\u8BBE\u4E3A\u9ED8\u8BA4\u89D2\u8272","ok"),await this.load()}catch(t){D(Z(t),"err")}finally{this.busy=""}},async cloneCard(e){this.busy="clone"+e.id;try{let t=await Y("rcbot.card.clone",{id:e.id});D("\u5DF2\u590D\u5236\u4E00\u4EFD","ok"),await this.load(),t&&t.id&&this.pick(this.list.find(i=>i.id===t.id)||null)}catch(t){D(Z(t),"err")}finally{this.busy=""}},async del(e){if(confirm("\u5220\u9664\u89D2\u8272\u5361\u7247\u300C"+(e.name||e.id)+`\u300D\uFF1F

\u7528\u5230\u5B83\u7684\u4F1A\u8BDD\u4F1A\u56DE\u843D\u5230\u9ED8\u8BA4\u89D2\u8272\u3002`)){this.busy="del"+e.id;try{await Y("rcbot.card.delete",{id:e.id}),D("\u5DF2\u5220\u9664","ok"),this.cur&&this.cur.id===e.id&&(this.cur=null),await this.load()}catch(t){D(Z(t),"err")}finally{this.busy=""}}},async exportJson(e){try{let t=await Y("rcbot.card.export",{id:e.id}),i=new Blob([t&&t.json||JSON.stringify(e,null,2)],{type:"application/json"}),s=document.createElement("a");s.href=URL.createObjectURL(i),s.download="card-"+String(e.name||e.id).replace(/[^\w一-龥-]/g,"_")+".json",s.click(),setTimeout(()=>URL.revokeObjectURL(s.href),3e3),D("\u5DF2\u5BFC\u51FA\u5361\u7247 JSON","ok")}catch(t){D(Z(t),"err")}},importJson(){let e=document.createElement("input");e.type="file",e.accept="application/json,.json",e.onchange=async()=>{let t=e.files&&e.files[0];if(t)try{let i=await t.text(),s=await Y("rcbot.card.import",{json:i});D("\u5DF2\u5BFC\u5165\uFF1A"+(s&&s.name||"\u89D2\u8272\u5361\u7247"),"ok"),await this.load(),s&&s.id&&this.pick(this.list.find(n=>n.id===s.id)||null)}catch(i){D(Z(i),"err")}},e.click()}},template:`
  <div class="rcq-split" :style="memoryOpen ? { gridTemplateColumns: '1fr' } : null">
    <!-- \u5DE6\uFF1A\u5361\u7247\u5217\u8868 -->
    <div class="rcq-pnl flat" v-if="!memoryOpen">
      <div class="rcq-ph" style="padding:14px 16px 0;margin-bottom:10px">
        <b>\u89D2\u8272\u5361\u7247</b><span class="sp"></span>
        <button class="btn btn-sm" @click="importJson">\u5BFC\u5165</button>
        <button class="btn btn-sm btn-primary" @click="add">\u65B0\u5EFA</button>
      </div>
      <div class="rcq-list cd-grid">
        <div class="cd-card" v-for="c in list" :key="c.id"
          :class="{ on: cur && cur.id === c.id }" @click="pick(c)">
          <div class="cdc-cover" :style="coverStyle(c)">
            <span class="cdc-fallback" v-if="!assetSrc(c, 'cover')">{{ (c.name || '?').slice(0, 1) }}</span>
          </div>
          <img v-if="avatarSrc(c)" class="cdc-ava" :src="avatarSrc(c)" alt=""
            @error="$event.target.style.display='none'" />
          <div class="cdc-body">
            <div class="cdc-name">{{ c.name || '\u672A\u547D\u540D' }}</div>
            <div class="cdc-tag">{{ c.tagline || (c.prompt || '').slice(0, 40) }}</div>
            <div class="cdc-badges">
              <span class="cd-tag" v-if="c.id === def">\u9ED8\u8BA4</span>
              <span class="cd-tag draft" v-if="c.status !== 'published'">\u8349\u7A3F</span>
              <span class="cd-tag v">v{{ c.version || 1 }}</span>
            </div>
          </div>
        </div>
        <div v-if="!list.length" class="rcq-empty" style="grid-column:1/-1">
          <b>\u263A</b>\u8FD8\u6CA1\u6709\u89D2\u8272\u5361\u7247\uFF0C\u70B9\u300C\u65B0\u5EFA\u300D\u52A0\u4E00\u4E2A</div>
      </div>
    </div>

    <!-- \u53F3\uFF1A\u8BB0\u5FC6\u661F\u7A7A -->
    <div class="rcq-pnl" v-if="cur && memoryOpen">
      <div class="rcq-ph">
        <button class="btn btn-sm" @click="backToList">\u2190 \u5361\u7247</button>
        <b style="margin-left:8px">{{ cur.name || '\u89D2\u8272' }} \xB7 \u8BB0\u5FC6</b><span class="sp"></span>
        <span class="rcq-hint" v-if="mem"> \xB7 {{ mem.total }} \u9897\u661F \xB7 {{ (mem.main || []).length }} \u4E3B\u661F \xB7 \u5783\u573E\u573A {{ mem.junk || 0 }}</span>
      </div>

      <!-- \u5361\u7247\u672C\u4F53\uFF08\u5DF2\u5E76\u5165\u8BB0\u5FC6\uFF0C\u4E0D\u518D\u5C55\u793A\uFF09 -->
      <div class="cd-hero" v-if="false" :class="{ grad: !assetSrc(cur, 'cover') }">
        <div class="cdh-cover" :style="coverStyle(cur)"></div>
        <div class="cdh-inner">
          <div class="cdh-ava">
            <img v-if="assetSrc(cur, 'avatar')" :src="assetSrc(cur, 'avatar')" alt="" />
            <span v-else>{{ (cur.name || '?').slice(0, 1) }}</span>
          </div>
          <div class="cdh-title">
            <div class="cdh-name">{{ cur.name || '\u672A\u547D\u540D' }}</div>
            <div class="cdh-alias" v-if="cur.alias && cur.alias.length">{{ cur.alias.join(' / ') }}</div>
            <div class="cdh-tag">{{ cur.tagline || '\uFF08\u8FD8\u6CA1\u6709\u7B80\u4ECB\uFF09' }}</div>
            <div class="cdh-badges">
              <span class="cd-tag" v-if="cur.id === def">\u9ED8\u8BA4\u89D2\u8272</span>
              <span class="cd-tag draft" v-if="cur.status !== 'published'">\u8349\u7A3F</span>
              <span class="cd-tag v">v{{ cur.version || 1 }}</span>
            </div>
          </div>
        </div>
        <div class="cdh-sections" v-if="(cur.greetings || []).length || (cur.examples || []).length || (cur.lorebook || []).length">
          <div class="cdh-sec" v-if="(cur.greetings || []).length">
            <b>\u5F00\u573A\u767D</b>
            <div class="cdh-line" v-for="(g, i) in cur.greetings" :key="'g' + i">\u300C{{ g }}\u300D</div>
          </div>
          <div class="cdh-sec" v-if="(cur.examples || []).length">
            <b>\u793A\u4F8B\u5BF9\u8BDD</b>
            <div class="cdh-ex" v-for="(ex, i) in cur.examples" :key="'e' + i">
              <div class="u">\u203A {{ ex.user }}</div>
              <div class="a">{{ ex.assistant }}</div>
            </div>
          </div>
          <div class="cdh-sec" v-if="(cur.lorebook || []).length">
            <b>\u4E16\u754C\u4E66</b>
            <div class="cdh-lore" v-for="(l, i) in cur.lorebook" :key="'l' + i">
              <span class="k">{{ (l.keys || []).join('\u3001') }}</span>{{ l.content }}
            </div>
          </div>
        </div>
      </div>

      <div class="cd-tabs" v-if="false">
        <button :class="{ on: section === 'basic' }" @click="section = 'basic'">\u5F62\u8C61</button>
        <button :class="{ on: section === 'content' }" @click="section = 'content'">\u5185\u5BB9</button>
        <button :class="{ on: section === 'behavior' }" @click="section = 'behavior'">\u884C\u4E3A</button>
        <button :class="{ on: section === 'memory' }" @click="openSection('memory')">\u8BB0\u5FC6</button>
      </div>

      <!-- \u5F62\u8C61 -->
      <div class="rcq-form" v-if="false">
        <label class="rcq-fi wide"><span>\u540D\u79F0</span>
          <input class="input" v-model="cur.name" @input="dirty = true" placeholder="\u4F8B\u5982\uFF1A\u96E8\u54AF" />
        </label>
        <label class="rcq-fi wide"><span>\u4E00\u53E5\u8BDD\u7B80\u4ECB</span>
          <input class="input" v-model="cur.tagline" @input="dirty = true"
            placeholder="\u5217\u8868\u9875\u663E\u793A\u7684\u90A3\u53E5\u8BDD" />
        </label>
        <label class="rcq-fi wide"><span>\u5C01\u9762\u56FE</span>
          <input class="input" v-model="cur.cover" @input="dirty = true"
            placeholder="https://\u2026 \u6216 cards/<\u5361\u7247ID>/cover.jpg" />
        </label>
        <label class="rcq-fi wide"><span>\u5934\u50CF</span>
          <input class="input" v-model="cur.avatar" @input="dirty = true"
            placeholder="https://\u2026 \u6216 cards/<\u5361\u7247ID>/avatar.png" />
        </label>
        <label class="rcq-fi wide"><span>\u7ACB\u7ED8</span>
          <input class="input" v-model="cur.portrait" @input="dirty = true"
            placeholder="https://\u2026 \u6216 cards/<\u5361\u7247ID>/portrait.png" />
        </label>
        <div class="rcq-hint wide" style="width:100%;margin:-4px 0 6px">
          \u586B\u76F8\u5BF9\u5A92\u4F53\u76EE\u5F55\u7684\u8DEF\u5F84\uFF08\u5982 cards/&lt;\u5361\u7247ID&gt;/cover.jpg\uFF09\uFF1D \u56FE\u7247\u7531\u9762\u677F\u672C\u673A\u6258\u7BA1\uFF0C\u6C38\u4E0D\u5931\u6548\uFF1B
          \u586B http(s) \u5916\u94FE\u5219\u6BCF\u6B21\u90FD\u53BB\u7F51\u4E0A\u53D6\u3002\u4FDD\u5B58\u540E\u53EF\u5728\u4E0A\u9762\u9884\u89C8\u3002
        </div>
        <label class="rcq-fi"><span>\u72B6\u6001</span>
          <select class="input" v-model="cur.status" @change="dirty = true">
            <option value="draft">\u8349\u7A3F</option>
            <option value="published">\u5DF2\u53D1\u5E03</option>
          </select>
        </label>
        <label class="rcq-fi"><span>\u7248\u672C</span>
          <input class="input" v-model.number="cur.version" @input="dirty = true" type="number" min="1" />
        </label>
      </div>

      <!-- \u5185\u5BB9 -->
      <div class="rcq-form" v-if="false">
        <label class="rcq-fi wide"><span>\u7CFB\u7EDF\u63D0\u793A\u8BCD</span>
          <textarea class="rcq-ta tall" v-model="cur.prompt" @input="dirty = true"
            placeholder="\u63CF\u8FF0\u5B83\u7684\u8EAB\u4EFD\u3001\u8BED\u6C14\u3001\u8FB9\u754C\u3002\u4F8B\u5982\uFF1A\u4F60\u53EB\u5C0F\u96E8\uFF0C\u8BF4\u8BDD\u7B80\u77ED\u81EA\u7136\uFF0C\u4E0D\u7528\u656C\u8BED\uFF0C\u4E0D\u4E3B\u52A8\u63D0\u81EA\u5DF1\u662F AI\u3002"></textarea>
        </label>

        <div class="cd-blk">
          <div class="cd-blk-h"><b>\u5F00\u573A\u767D</b>
            <button class="btn btn-sm" @click="addGreeting">\u6DFB\u52A0\u4E00\u6761</button></div>
          <div class="cd-item" v-for="(g, i) in cur.greetings" :key="'g' + i">
            <textarea class="rcq-ta" v-model="cur.greetings[i]" @input="dirty = true"
              placeholder="\u8FDB\u5165\u4F1A\u8BDD\u65F6\u968F\u673A\u8BF4\u7684\u4E00\u53E5\u8BDD"></textarea>
            <button class="cd-x" title="\u5220\u9664" @click="rmGreeting(i)">\xD7</button>
          </div>
          <div class="rcq-hint" v-if="!(cur.greetings || []).length">\u8FD8\u6CA1\u6709\u5F00\u573A\u767D</div>
        </div>

        <div class="cd-blk">
          <div class="cd-blk-h"><b>\u793A\u4F8B\u5BF9\u8BDD</b>
            <button class="btn btn-sm" @click="addExample">\u6DFB\u52A0\u4E00\u7EC4</button></div>
          <div class="cd-item col" v-for="(ex, i) in cur.examples" :key="'e' + i">
            <div class="cd-row2">
              <input class="input" v-model="cur.examples[i].user" @input="dirty = true" placeholder="\u7528\u6237\u8BF4" />
              <input class="input" v-model="cur.examples[i].assistant" @input="dirty = true" placeholder="\u89D2\u8272\u56DE" />
              <button class="cd-x" title="\u5220\u9664" @click="rmExample(i)">\xD7</button>
            </div>
          </div>
          <div class="rcq-hint" v-if="!(cur.examples || []).length">\u8FD8\u6CA1\u6709\u793A\u4F8B</div>
        </div>

        <div class="cd-blk">
          <div class="cd-blk-h"><b>\u4E16\u754C\u4E66</b>
            <button class="btn btn-sm" @click="addLore">\u6DFB\u52A0\u4E00\u6761</button></div>
          <div class="cd-item col" v-for="(l, i) in cur.lorebook" :key="'l' + i">
            <div class="cd-row2">
              <input class="input" :value="loreKeys(l)" @input="setLoreKeys(l, $event.target.value); dirty = true"
                placeholder="\u89E6\u53D1\u5173\u952E\u8BCD\uFF08\u987F\u53F7\u5206\u9694\uFF09" />
              <button class="cd-x" title="\u5220\u9664" @click="rmLore(i)">\xD7</button>
            </div>
            <textarea class="rcq-ta" v-model="cur.lorebook[i].content" @input="dirty = true"
              placeholder="\u8FD9\u6761\u80CC\u666F\u8BBE\u5B9A"></textarea>
          </div>
          <div class="rcq-hint" v-if="!(cur.lorebook || []).length">\u8FD8\u6CA1\u6709\u4E16\u754C\u4E66\u6761\u76EE</div>
        </div>

        <label class="rcq-fi wide"><span>\u7981\u5219\uFF08\u6BCF\u884C\u4E00\u6761\uFF09</span>
          <textarea class="rcq-ta" :value="taboosText()" @input="setTaboosText($event.target.value); dirty = true"
            placeholder="\u4E0D\u8981\u8BF4\u7684\u8BDD\u3001 \u4E0D\u8981\u505A\u7684\u4E8B"></textarea>
        </label>
      </div>

      <!-- \u884C\u4E3A -->
      <div class="rcq-form" v-if="false">
        <label class="rcq-fi wide"><span>\u6A21\u578B\u63D0\u4F9B\u5546</span>
          <select class="input" v-model="cur.model.provider_id" @change="dirty = true">
            <option value="">\uFF08\u8DDF\u968F\u8D26\u53F7\u9ED8\u8BA4\uFF09</option>
            <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.name || p.id }}</option>
          </select>
        </label>
        <label class="rcq-fi wide"><span>\u6A21\u578B\u540D</span>
          <input class="input" v-model="cur.model.model" @input="dirty = true" placeholder="\u7559\u7A7A = \u7528\u63D0\u4F9B\u5546\u7684\u9ED8\u8BA4\u6A21\u578B" />
        </label>
        <label class="rcq-fi"><span>\u6E29\u5EA6</span>
          <input class="input" type="number" step="0.1" min="0" max="2"
            v-model.number="cur.style.temperature" @input="dirty = true" />
        </label>
        <label class="rcq-fi"><span>\u6700\u5927 tokens</span>
          <input class="input" type="number" step="64" min="64"
            v-model.number="cur.style.max_tokens" @input="dirty = true" />
        </label>
        <label class="rcq-fi"><span>\u6700\u591A\u5B57\u6570</span>
          <input class="input" type="number" step="10" min="0" placeholder="\u4E0D\u9650"
            v-model.number="cur.style.max_chars" @input="dirty = true" />
        </label>
        <label class="rcq-fi"><span>\u5141\u8BB8 emoji</span>
          <label class="switch">
            <input type="checkbox" :checked="!!cur.style.allow_emoji"
              @change="cur.style.allow_emoji = $event.target.checked; dirty = true" />
            <span class="slider"></span>
          </label>
        </label>
        <label class="rcq-fi"><span>\u4E0A\u4E0B\u6587\u8F6E\u6570</span>
          <input class="input" type="number" min="1"
            v-model.number="cur.context.keep_rounds" @input="dirty = true" />
        </label>
            <label class="rcq-fi"><span>\u6C14\u6CE1\u8272</span>
          <input class="input" v-model="cur.style.color" @input="dirty = true" placeholder="#12b7f5" />
        </label>
        <label class="rcq-fi"><span>\u56DE\u590D\u65B9\u5F0F</span>
          <select class="input" v-model="cur.style.reply_mode" @change="dirty = true">
            <option value="auto">\u81EA\u52A8\uFF08\u957F\u4E86\u62C6\u591A\u6761\uFF09</option>
            <option value="single">\u603B\u662F\u5355\u6761</option>
            <option value="multi">\u5C3D\u91CF\u591A\u6761\u77ED\u53E5</option>
          </select>
        </label>
        <label class="rcq-fi"><span>\u6BCF\u6761\u6700\u591A\u5B57\u6570</span>
          <input class="input" type="number" min="8" max="200"
            v-model.number="cur.style.part_chars" @input="dirty = true" />
        </label>
        <label class="rcq-fi"><span>\u6700\u591A\u51E0\u6761</span>
          <input class="input" type="number" min="1" max="10"
            v-model.number="cur.style.max_parts" @input="dirty = true" />
        </label>
        <label class="rcq-fi"><span>\u53D1\u9001\u95F4\u9694\uFF08\u79D2\uFF09</span>
          <input class="input" type="number" step="0.05" min="0" max="2"
            v-model.number="cur.style.part_delay" @input="dirty = true" />
        </label>
      </div>

      <div class="rcq-sec" v-if="false">
        <div class="rcq-ph" style="margin-bottom:8px"><b>\u5173\u952E\u8BCD\u5FC5\u56DE</b>
          <span class="rcq-hint">\u547D\u4E2D\u5173\u952E\u8BCD\u76F4\u63A5\u56DE\u56FA\u5B9A\u6587\u6848\uFF0C\u4E0D\u8C03\u6A21\u578B\u3001\u4E0D\u53D7 AI \u5F00\u5173\u5F71\u54CD</span></div>
        <div v-for="(k, i) in (cur.keywords || [])" :key="i" class="rcq-flex"
          style="gap:8px;margin-bottom:8px;flex-wrap:wrap">
          <input class="input" style="flex:1;min-width:130px" v-model="k.match"
            placeholder="\u5173\u952E\u8BCD" @input="dirty = true" />
          <input class="input" style="flex:2;min-width:200px" v-model="k.reply"
            placeholder="\u56DE\u590D\u5185\u5BB9\uFF0C\u652F\u6301 {nick}" @input="dirty = true" />
          <select class="input" style="width:110px" v-model="k.mode" @change="dirty = true">
            <option value="contains">\u5305\u542B</option>
            <option value="exact">\u5B8C\u5168\u5339\u914D</option>
          </select>
          <label class="rcq-hint"><input type="checkbox" v-model="k.require_at"
            @change="dirty = true" /> \u9700 @</label>
          <label class="rcq-hint"><input type="checkbox" v-model="k.enabled"
            @change="dirty = true" /> \u542F\u7528</label>
          <button class="btn btn-sm" @click="rmKw(i)">\u5220\u9664</button>
        </div>
        <button class="btn btn-sm" @click="addKw">+ \u6DFB\u52A0\u5173\u952E\u8BCD</button>
        <div class="rcq-note" v-if="!(cur.keywords || []).length">
          \u4F8B\u5982\u300C\u6253\u5361\u300D\u2192\u300C\u6253\u5361\u6210\u529F\uFF0C\u4ECA\u5929\u4E5F\u8981\u52A0\u6CB9\u300D\uFF1B\u7FA4\u91CC\u9ED8\u8BA4\u9700\u8981 @ \u673A\u5668\u4EBA\uFF0C\u79C1\u804A\u4E0D\u9700\u8981\u3002
        </div>
      </div>

      <div class="rcq-sec" v-if="section === 'memory'" style="position:relative">
        <div class="rcq-flex" style="justify-content:space-between;align-items:center;margin-bottom:8px">
          <div><b>\u8BB0\u5FC6\u661F\u7A7A</b>
            <span class="rcq-hint" v-if="mem"> \xB7 {{ mem.total }} \u9897\u661F \xB7 {{ (mem.main || []).length }} \u4E3B\u661F \xB7 \u5783\u573E\u573A {{ mem.junk || 0 }}</span>
            <span class="rcq-hint" v-else-if="memLoading">\u661F\u57DF\u52A0\u8F7D\u4E2D\u2026</span>
          </div>
          <div class="rcq-flex" style="gap:6px">
            <select class="input" style="width:190px" v-model="memScopeKey" @change="changeScope">
              <option value="global">\u5168\u5C40\u8BB0\u5FC6</option>
              <optgroup label="\u7FA4\u804A" v-if="memScopes.groups.length">
                <option v-for="g in memScopes.groups" :key="g.key" :value="g.key">{{ g.label }}</option>
              </optgroup>
              <optgroup label="\u79C1\u804A" v-if="memScopes.privates.length">
                <option v-for="p in memScopes.privates" :key="p.key" :value="p.key">{{ p.label }}</option>
              </optgroup>
            </select>
            <input class="input" style="width:170px" v-model="memQuery" @input="searchMem"
              @keyup.enter="openFirstHit" @keyup.esc="clearSearch" placeholder="\u641C\u7D22\u8BB0\u5FC6\u2026" />
            <button v-if="memQuery" class="btn btn-sm" @click="clearSearch">\xD7</button>
            <span class="rcq-hint" v-if="memQuery">{{ memHits.length }} \u6761</span>
            <button v-if="memHits.length" class="btn btn-sm" @click="openHit(-1)">\u2039</button>
            <button v-if="memHits.length" class="btn btn-sm" @click="openHit(1)">\u203A</button>
            <button class="btn btn-sm" @click="toggleStats">\u7EDF\u8BA1</button>
            <button class="btn btn-sm" @click="consolidateMem">\u5DE9\u56FA</button>
            <button class="btn btn-sm" @click="openKeywords">\u5173\u952E\u8BCD</button>
            <label class="rcq-hint"><input type="checkbox" v-model="showJunk"
              @change="toggleJunk" /> \u663E\u793A\u5783\u573E\u573A</label>
            <button class="btn btn-sm" @click="loadMemory">\u5237\u65B0</button>
            <button class="btn btn-sm" @click="fitMem">\u9002\u914D</button>
          </div>
        </div>
        <canvas ref="memCanvas" @mousedown="memDown" @mousemove="memMove" @mouseup="memUp"
          @mouseleave="memUp" @click="memClick" @wheel="memWheel"
          style="width:100%;height:calc(100vh - 210px);min-height:560px;border-radius:12px;display:block;cursor:grab;background:#05080f;border:1px solid rgba(120,160,220,.18)"></canvas>
        <div class="rcq-hint" style="margin-top:6px">\u62D6\u52A8\u5E73\u79FB \xB7 \u6EDA\u8F6E\u7F29\u653E \xB7 \u70B9\u51FB\u661F\u661F\u67E5\u770B \xB7 \u6697\u661F\u4F1A\u6C89\u5165\u5783\u573E\u573A</div>
        <div v-if="showKeywords" style="position:absolute;inset:0;background:#070c14;z-index:30;border-radius:12px;padding:14px;overflow:auto;border:1px solid rgba(120,160,220,.25)">
          <div class="rcq-flex" style="justify-content:space-between;align-items:center;gap:8px;margin-bottom:10px">
            <b style="color:#f0f6ff">\u5173\u952E\u8BCD\u7BA1\u7406 \xB7 {{ kwList.length }} \u6761</b>
            <span class="rcq-hint" style="color:#e6b85c">\u5305\u542B\u5339\u914D \xB7 \u4EC5\u5BF9\u5DF2\u542F\u7528\u7684\u7FA4\u751F\u6548</span>
            <div class="rcq-flex" style="gap:6px;align-items:center">
              <input class="input" style="width:160px" v-model="kwQuery" placeholder="\u641C\u7D22\u5173\u952E\u8BCD/\u56DE\u590D\u2026" />
              <span class="rcq-hint" style="color:#9fb2c8">{{ kwFiltered().length }} \u6761</span>
              <button class="btn btn-sm" @click="bulkKw(true)">\u5168\u90E8\u542F\u7528</button>
              <button class="btn btn-sm" @click="bulkKw(false)">\u5168\u90E8\u505C\u7528</button>
              <button class="btn btn-sm" @click="showKeywords = false">\u5173\u95ED</button>
            </div>
          </div>
          <div class="rcq-flex" style="gap:6px;margin-bottom:10px;flex-wrap:wrap;padding:8px;border:1px solid rgba(120,160,220,.2);border-radius:8px">
            <input class="input" style="width:150px" v-model="kwNew.match" placeholder="\u65B0\u5173\u952E\u8BCD" />
            <input class="input" style="flex:1;min-width:200px" v-model="kwNew.reply" placeholder="\u515C\u5E95\u56DE\u590D\uFF08\u6A21\u578B\u5931\u8D25\u65F6\u7528\uFF09" />
            <span style="width:100px">\u5305\u542B\u5339\u914D</span>
            <button class="btn btn-sm" @click="addKeyword">\u6DFB\u52A0</button>
          </div>
          <div class="rcq-flex" style="font-size:11px;color:#8fa4bd;padding:0 4px 6px;gap:6px">
            <span style="width:150px">\u5173\u952E\u8BCD</span><span style="flex:1">\u515C\u5E95\u56DE\u590D\uFF08\u6A21\u578B\u5931\u8D25\u65F6\u7528\uFF09</span>
            <span style="width:100px">\u5339\u914D</span>
            <span style="width:44px">\u542F\u7528</span><span style="width:90px">\u64CD\u4F5C</span>
          </div>
          <div v-for="k in kwFiltered().slice(0, kwLimit)" :key="k.id"
            class="rcq-flex" style="gap:6px;align-items:center;padding:4px 0;border-top:1px solid rgba(120,160,220,.08)">
            <input class="input" style="width:150px" v-model="k.match" @change="saveKw(k)" />
            <input class="input" style="flex:1;min-width:160px" v-model="k.reply" @change="saveKw(k)" />
            <span style="width:100px;color:#9fb2c8">\u5305\u542B</span>
            <input type="checkbox" style="width:44px" v-model="k.enabled" @change="saveKw(k)" />
            <button class="btn btn-sm" style="width:90px;color:#f5534f" @click="delKw(k)">\u5220\u9664</button>
          </div>
          <div v-if="kwFiltered().length > kwLimit" style="text-align:center;margin-top:10px">
            <button class="btn btn-sm" @click="kwLimit += 100">\u52A0\u8F7D\u66F4\u591A\uFF08\u5269\u4F59 {{ kwFiltered().length - kwLimit }}\uFF09</button>
          </div>
        </div>
        <div v-if="showStats && memStats" style="position:absolute;left:12px;top:44px;width:280px;max-height:470px;overflow:auto;background:rgba(10,16,26,.97);border:1px solid rgba(130,170,230,.4);border-radius:10px;padding:12px;box-shadow:0 8px 30px rgba(0,0,0,.6);color:#dbe7f5">
          <div class="rcq-flex" style="justify-content:space-between;align-items:center">
            <b style="color:#f0f6ff">\u8BB0\u5FC6\u7EDF\u8BA1</b>
            <button class="btn btn-sm" @click="showStats = false">\xD7</button>
          </div>
          <div class="rcq-hint" style="margin:8px 0;color:#9fb2c8">
            \u5171 {{ memStats.total }} \u6761 \xB7 {{ memStats.chars }} \u5B57 \xB7 \u8FD1 7 \u5929 +{{ memStats.recent7d }}
          </div>
          <div v-for="(c, t) in memStats.types" :key="t" class="rcq-flex"
            style="justify-content:space-between;font-size:12px;padding:3px 0;color:#dbe7f5">
            <span>{{ memName(t) }}</span><b>{{ c }}</b>
          </div>
          <div class="rcq-hint" style="margin-top:8px;color:#9fb2c8">
            \u72B6\u6001\uFF1A\u6B63\u5E38 {{ (memStats.states && memStats.states.active) || 0 }} \xB7
            \u4F11\u7720 {{ (memStats.states && memStats.states.dormant) || 0 }} \xB7
            \u5783\u573E\u573A {{ (memStats.states && memStats.states.junk) || 0 }}
          </div>
          <div class="rcq-hint" style="color:#9fb2c8">
            \u8303\u56F4\uFF1A\u5168\u5C40 {{ (memStats.scopes && memStats.scopes.global) || 0 }} \xB7
            \u7FA4 {{ (memStats.scopes && memStats.scopes.group) || 0 }} \xB7
            \u79C1\u804A {{ (memStats.scopes && memStats.scopes.private) || 0 }}
          </div>
        </div>
        <div v-if="memSel" style="position:absolute;right:10px;top:44px;width:330px;max-height:470px;overflow:auto;background:rgba(14,20,30,.96);border:1px solid rgba(120,160,220,.3);border-radius:10px;padding:12px;box-shadow:0 8px 30px rgba(0,0,0,.5)">
          <div class="rcq-flex" style="justify-content:space-between;align-items:center">
            <b>{{ memName(memSel.type) }}</b>
            <button class="btn btn-sm" @click="memSel = null">\xD7</button>
          </div>
          <textarea class="input" v-model="memSel.content"
            style="width:100%;height:150px;margin:10px 0;font-size:13px;line-height:1.6;resize:vertical"></textarea>
          <div class="rcq-hint">\u91CD\u8981\u5EA6
            <input class="input" type="number" step="0.05" min="0" max="1"
              v-model.number="memSel.importance" style="width:70px;margin:0 6px" />
            \xB7 \u4F7F\u7528 {{ memSel.use_count || 0 }} \u6B21 \xB7 {{ memState(memSel.state) }}
          </div>
          <div class="rcq-flex" style="gap:8px;margin-top:10px">
            <button class="btn btn-sm" @click="saveMem">\u4FDD\u5B58\u4FEE\u6539</button>
            <button class="btn btn-sm" @click="pinMem">{{ memSel.pinned ? '\u53D6\u6D88\u7F6E\u9876' : '\u7F6E\u9876' }}</button>
            <button class="btn btn-sm" @click="delMem">\u79FB\u5165\u5783\u573E\u573A</button>
          </div>
        </div>
      </div>

      <div class="rcq-flex" style="margin-top:12px" v-if="false">
        <button class="btn btn-sm" @click="setDefault(cur)">\u8BBE\u4E3A\u9ED8\u8BA4\u89D2\u8272</button>
        <button class="btn btn-sm" style="color:var(--err,#f5534f)"
          :disabled="busy === 'del' + cur.id" @click="del(cur)">\u5220\u9664</button>
        <span class="rcq-hint" style="margin-left:auto">\u5361\u7247 v{{ cur.version || 1 }} \xB7 {{ cur.status === 'published' ? '\u5DF2\u53D1\u5E03' : '\u8349\u7A3F' }}</span>
      </div>
      <div class="rcq-note" v-if="false">
        \u89D2\u8272\u5361\u7247\u662F\u300C\u5B9A\u4E49\u300D\uFF0C\u8D26\u53F7\u548C\u4F1A\u8BDD\u53EA\u5F15\u7528\u5B83 \u2014\u2014 \u6539\u5361\u7247\u4E0D\u4F1A\u5F71\u54CD\u5DF2\u7ECF\u4EA7\u751F\u7684\u5386\u53F2\u4F1A\u8BDD\u3002
        \u60F3\u7ED9\u522B\u7684\u673A\u5668\u4EBA\u7528\uFF0C\u76F4\u63A5\u300C\u5BFC\u51FA\u300D\u6210 JSON \u53D1\u8FC7\u53BB\uFF0C\u5BF9\u65B9\u300C\u5BFC\u5165\u300D\u5373\u53EF\u3002
      </div>
    </div>

    <div class="rcq-pnl" v-else>
      <div class="rcq-empty"><b>\u263A</b>\u5DE6\u8FB9\u9009\u4E00\u5F20\u5361\u7247\uFF0C\u6216\u8005\u65B0\u5EFA\u4E00\u5F20</div>
    </div>
  </div>`},Bm={data(){return{S:yt,list:[],stats:{},defPersona:"",defProvider:"",personas:[],providers:[],cur:null,detail:null,ctx:null,filter:"all",kw:"",busy:"",err:"",limit:60}},computed:{shown(){let e=this.kw.trim().toLowerCase();return this.list.filter(t=>this.filter==="group"&&t.kind!=="group"||this.filter==="private"&&t.kind==="group"||this.filter==="off"&&t.enabled!==0||this.filter==="on"&&t.enabled===0?!1:e?((t.display||"")+" "+(t.id||"")+" "+(t.target_id||"")).toLowerCase().indexOf(e)>=0:!0)},enabledCount(){return this.list.filter(e=>e.enabled!==0).length},usedPct(){let e=this.ctx;return!e||!e.budget?0:Math.min(100,Math.round(e.est_tokens/e.budget*100))},barClass(){return this.usedPct>=90?"max":this.usedPct>=70?"hi":""}},async mounted(){await this.load()},methods:{fmtTime:Nm,fmtNum:rn,async load(){this.busy="load";try{let e=await Y("rcbot.sessions");this.list=e&&e.items||[],this.stats=e&&e.stats||{},this.defPersona=e&&e.default_persona||"",this.defProvider=e&&e.default_provider||"";let t=await Y("rcbot.personas");this.personas=t&&t.items||[];let i=await Y("rcbot.providers");if(this.providers=i&&i.items||[],this.cur){let s=this.list.find(n=>n.id===this.cur.id);s&&(this.cur=s)}}catch(e){this.err=Z(e)}finally{this.busy=""}},async open(e){this.cur=e,this.busy="open";try{this.detail=await Y("rcbot.session.get",{id:e.id,limit:this.limit}),this.ctx=await Y("rcbot.context",{id:e.id})}catch(t){D(Z(t),"err")}finally{this.busy=""}},async syncCatalog(){if(confirm(`\u4ECE QQ \u62C9\u53D6\u5168\u90E8\u7FA4\u804A\u4E0E\u597D\u53CB\uFF1F

\u62C9\u5230\u7684\u4F1A\u8BDD\u9ED8\u8BA4\u90FD\u662F\u300C\u4E0D\u542F\u7528\u300D\uFF0C\u9700\u8981\u4F60\u81EA\u5DF1\u6253\u5F00\u5F00\u5173\u3002`)){this.busy="sync";try{let e=await Y("rcbot.session.catalog",{});D("\u5DF2\u62C9\u53D6\uFF1A\u7FA4 "+(e.groups||0)+" \u4E2A\u3001\u597D\u53CB "+(e.friends||0)+" \u4E2A\uFF0C\u65B0\u589E\u4F1A\u8BDD "+(e.new||0)+" \u4E2A","ok"),await this.load()}catch(e){D(Z(e),"err")}finally{this.busy=""}}},async toggle(e,t){let i=e.enabled;e.enabled=t?1:0;try{await Ue("rcbot.session.save",{id:e.id,enabled:t?1:0})}catch(s){e.enabled=i,D(Z(s),"err")}},async bulk(e){if(!(e&&!confirm(`\u542F\u7528\u5168\u90E8\u4F1A\u8BDD\uFF1F

\u673A\u5668\u4EBA\u4F1A\u5728\u8FD9\u4E9B\u7FA4\u91CC\u81EA\u52A8\u56DE\u590D\uFF08\u7FA4\u91CC\u4ECD\u9700 @ \u6216\u5524\u9192\u524D\u7F00\uFF09\u3002`))&&!(!e&&!confirm("\u505C\u7528\u5168\u90E8\u4F1A\u8BDD\uFF1F\u673A\u5668\u4EBA\u5C06\u4E0D\u518D\u81EA\u52A8\u56DE\u590D\u3002"))){this.busy="bulk";try{let t=await Y("rcbot.session.bulk",{enabled:e?1:0});D((e?"\u5DF2\u542F\u7528 ":"\u5DF2\u505C\u7528 ")+(t.changed||0)+" \u4E2A\u4F1A\u8BDD","ok"),await this.load()}catch(t){D(Z(t),"err")}finally{this.busy=""}}},async reloadDetail(){if(this.cur)try{this.detail=await Y("rcbot.session.get",{id:this.cur.id,limit:this.limit}),this.ctx=await Y("rcbot.context",{id:this.cur.id})}catch(e){D(Z(e),"err")}},async patch(e,t){if(this.cur){this.busy="p"+e;try{let i={id:this.cur.id};i[e]=t,await Ue("rcbot.session.save",i),D("\u5DF2\u66F4\u65B0","ok"),await this.load(),await this.reloadDetail()}catch(i){D(Z(i),"err")}finally{this.busy=""}}},async clear(){if(this.cur&&confirm("\u6E05\u7A7A\u300C"+(this.cur.display||this.cur.id)+"\u300D\u7684\u4E0A\u4E0B\u6587\uFF1F\u6D88\u606F\u4F1A\u5220\u6389\uFF0C\u4F1A\u8BDD\u4FDD\u7559\u3002")){this.busy="clear";try{await Ue("rcbot.session.clear",{id:this.cur.id}),D("\u4E0A\u4E0B\u6587\u5DF2\u6E05\u7A7A","ok"),await this.load(),await this.reloadDetail()}catch(e){D(Z(e),"err")}finally{this.busy=""}}},async del(){if(this.cur&&confirm("\u5220\u9664\u4F1A\u8BDD\u300C"+(this.cur.display||this.cur.id)+"\u300D\uFF1F\u6D88\u606F\u548C\u6458\u8981\u4E00\u8D77\u5220\u3002")){this.busy="del";try{await Ue("rcbot.session.delete",{id:this.cur.id}),D("\u5DF2\u5220\u9664","ok"),this.cur=null,this.detail=null,this.ctx=null,await this.load()}catch(e){D(Z(e),"err")}finally{this.busy=""}}},personaName(e){if(!e)return"\u9ED8\u8BA4";let t=this.personas.find(i=>i.id===e);return t?t.name:e},providerName(e){if(!e)return"\u9ED8\u8BA4";let t=this.providers.find(i=>i.id===e);return t?t.label||t.id:e}},template:`
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-split">
      <div class="rcq-pnl flat">
        <div class="rcq-ph" style="padding:14px 16px 0;margin-bottom:10px">
          <b>\u4F1A\u8BDD</b>
          <span class="rcq-hint">{{ stats.sessions || 0 }} \u4E2A \xB7 \u6D88\u606F {{ fmtNum(stats.messages || 0) }}</span>
          <span class="sp"></span>
          <button class="btn btn-sm" :disabled="!!busy" @click="syncCatalog">
            {{ busy === 'sync' ? '\u62C9\u53D6\u4E2D\u2026' : '\u62C9\u53D6\u7FA4\u804A/\u79C1\u804A' }}</button>
          <button class="btn btn-sm" :disabled="!!busy" @click="load">\u5237\u65B0</button>
        </div>
        <div class="rcq-flex" style="padding:0 16px 8px">
          <button class="btn btn-sm" :class="filter === 'all' ? 'btn-primary' : ''" @click="filter = 'all'">\u5168\u90E8</button>
          <button class="btn btn-sm" :class="filter === 'group' ? 'btn-primary' : ''" @click="filter = 'group'">\u7FA4\u804A</button>
          <button class="btn btn-sm" :class="filter === 'private' ? 'btn-primary' : ''" @click="filter = 'private'">\u79C1\u804A</button>
          <button class="btn btn-sm" :class="filter === 'on' ? 'btn-primary' : ''" @click="filter = 'on'">\u5DF2\u542F\u7528</button>
          <button class="btn btn-sm" :class="filter === 'off' ? 'btn-primary' : ''" @click="filter = 'off'">\u5DF2\u505C\u7528</button>
          <input class="input" style="flex:1;min-width:90px;padding:4px 10px;font-size:12px"
            v-model="kw" placeholder="\u641C\u4F1A\u8BDD" />
        </div>
        <div class="rcq-flex" style="padding:0 16px 8px;font-size:11.5px;color:var(--m)">
          <span>\u5DF2\u542F\u7528 <b>{{ enabledCount }}</b> / {{ list.length }}</span>
          <span class="sp"></span>
          <button class="btn btn-sm" :disabled="!!busy" @click="bulk(true)">\u5168\u90E8\u542F\u7528</button>
          <button class="btn btn-sm" :disabled="!!busy" @click="bulk(false)">\u5168\u90E8\u505C\u7528</button>
        </div>
        <div class="rcq-list">
          <div class="rcq-row click" v-for="s in shown" :key="s.id"
            :class="{ on: cur && cur.id === s.id }" @click="open(s)">
            <div class="main">
              <div class="t">
                <span class="tag-chip tag-chip-sm">{{ s.kind === 'group' ? '\u7FA4' : '\u79C1' }}</span>
                {{ s.display || s.target_id || s.id }}
                <span class="tag-chip tag-chip-sm" v-if="!s.talked">\u672A\u804A\u8FC7</span>
                <span class="tag-chip tag-chip-sm" v-if="s.enabled === 0">\u5DF2\u505C\u7528</span>
              </div>
              <div class="d">
                {{ s.msg_count || 0 }} \u6761 \xB7 {{ s.mode_label || '' }}
                <template v-if="s.persona_id"> \xB7 {{ personaName(s.persona_id) }}</template>
                \xB7 {{ fmtTime(s.last_at || s.updated_at) }}
              </div>
            </div>
            <div class="acts" @click.stop>
              <label class="switch" :title="s.enabled === 0 ? '\u542F\u7528\u8FD9\u4E2A\u4F1A\u8BDD' : '\u505C\u7528\u8FD9\u4E2A\u4F1A\u8BDD'">
                <input type="checkbox" :checked="s.enabled !== 0" :disabled="!!busy"
                  @change="toggle(s, $event.target.checked)" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div v-if="!shown.length" class="rcq-empty"><b>\u25A4</b>\u6CA1\u6709\u4F1A\u8BDD</div>
        </div>
      </div>

      <div v-if="cur">
        <div class="rcq-pnl">
          <div class="rcq-ph">
            <b>{{ cur.display || cur.target_id }}</b>
            <span class="tag-chip tag-chip-sm">{{ cur.kind === 'group' ? '\u7FA4\u804A' : '\u79C1\u804A' }}</span>
            <span class="tag-chip tag-chip-sm">{{ cur.mode_label || '' }}</span>
            <span class="sp"></span>
            <button class="btn btn-sm" :disabled="!!busy" @click="reloadDetail">\u5237\u65B0</button>
          </div>

          <div class="rcq-form">
            <label class="rcq-fi"><span>\u89D2\u8272\u5361\u7247</span>
              <select class="select" :value="cur.persona_id || ''" :disabled="!!busy"
                @change="patch('persona_id', $event.target.value)">
                <option value="">\u8DDF\u968F\u9ED8\u8BA4\uFF08{{ personaName(defPersona) }}\uFF09</option>
                <option v-for="p in personas" :key="p.id" :value="p.id">{{ p.name || p.id }}</option>
              </select>
            </label>
            <label class="rcq-fi"><span>\u6A21\u578B\u63D0\u4F9B\u5546</span>
              <select class="select" :value="cur.provider_id || ''" :disabled="!!busy"
                @change="patch('provider_id', $event.target.value)">
                <option value="">\u8DDF\u968F\u9ED8\u8BA4\uFF08{{ providerName(defProvider) }}\uFF09</option>
                <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.label || p.id }}</option>
              </select>
            </label>
            <div class="rcq-fi"><span>\u542F\u7528</span>
              <label class="switch">
                <input type="checkbox" :checked="cur.enabled !== 0" :disabled="!!busy"
                  @change="patch('enabled', $event.target.checked)" />
                <span class="slider"></span>
              </label>
            </div>
          </div>

          <div class="rcq-sec" v-if="ctx">
            <div class="rcq-flex" style="margin-bottom:4px">
              <span class="rcq-hint">\u4E0A\u4E0B\u6587\u5360\u7528</span>
              <span class="sp" style="margin-left:auto"></span>
              <span class="rcq-mono">{{ ctx.est_tokens }} / {{ ctx.budget }} tokens\uFF08{{ usedPct }}%\uFF09</span>
            </div>
            <div class="rcq-bar2"><i :class="barClass" :style="{ width: usedPct + '%' }"></i></div>
            <div class="rcq-note">
              \u9884\u7B97 = \u4E0A\u4E0B\u6587\u7A97\u53E3 \u2212 \u6700\u5927\u8F93\u51FA \u2212 \u7CFB\u7EDF\u63D0\u793A\u3002\u8D85\u4E86\u5C31\u6309\u300C\u4FDD\u7559\u6700\u8FD1\u6BD4\u4F8B\u300D\u538B\u7F29\u6210\u6458\u8981\u3002
            </div>
            <div class="rcq-flex" style="margin-top:10px">
              <button class="btn btn-sm" :disabled="!!busy" @click="clear">\u6E05\u7A7A\u4E0A\u4E0B\u6587</button>
              <button class="btn btn-sm btn-danger" :disabled="!!busy" @click="del">\u5220\u9664\u4F1A\u8BDD</button>
            </div>
          </div>
        </div>

        <div class="rcq-pnl" v-if="detail">
          <div class="rcq-ph"><b>\u6D88\u606F\u8BB0\u5F55</b><span class="sp"></span>
            <span class="rcq-hint">\u6700\u8FD1 {{ (detail.messages || []).length }} / \u5171 {{ detail.msg_count || 0 }} \u6761</span></div>

          <div v-if="detail.summary" class="rcq-pnl" style="background:var(--sf2);margin-bottom:12px">
            <div class="rcq-ph" style="margin-bottom:6px"><b>\u538B\u7F29\u6458\u8981</b>
              <span class="rcq-hint">\u65E7\u5BF9\u8BDD\u88AB\u538B\u6210\u4E86\u8FD9\u6BB5</span></div>
            <div style="font-size:12.5px;white-space:pre-wrap">{{ detail.summary }}</div>
          </div>

          <div class="rcq-msgs">
            <div class="rcq-msg" v-for="m in (detail.messages || [])" :key="m.id"
              :class="{ me: m.role === 'assistant' }">
              <div class="who">{{ m.role === 'assistant' ? '\u52A9\u624B' : (m.name || '\u7528\u6237') }}</div>
              <div class="body">{{ m.content }}</div>
            </div>
            <div v-if="!(detail.messages || []).length" class="rcq-empty"><b>\u25A4</b>\u8FD9\u4E2A\u4F1A\u8BDD\u8FD8\u6CA1\u6709\u6D88\u606F</div>
          </div>
        </div>
      </div>

      <div class="rcq-pnl" v-else>
        <div class="rcq-empty"><b>\u25A4</b>\u5DE6\u8FB9\u70B9\u4E00\u4E2A\u4F1A\u8BDD\u770B\u8BE6\u60C5</div>
      </div>
    </div>
  </div>`},Dm={data(){return{S:yt,list:[],def:"",cur:null,busy:"",err:"",dirty:!1,test:null,models:[],showKey:!1}},computed:{isNew(){return!!(this.cur&&this.cur.__new)}},async mounted(){await this.load()},methods:{async load(){try{let e=await Y("rcbot.providers");if(this.list=e&&e.items||[],this.def=e&&e.default||"",!this.cur)this.pick(this.list[0]||null);else if(!this.cur.__new&&!this.dirty){let t=this.list.find(i=>i.id===this.cur.id);t&&this.pick(t)}}catch(e){this.err=Z(e)}},pick(e){this.cur=e?Object.assign({type:"openai",timeout:120,enable:!0},e):null,this.dirty=!1,this.test=null,this.models=[]},add(){this.cur={id:"",label:"",type:"openai",api_base:"https://api.openai.com/v1",api_key:"",model:"",timeout:120,enable:!0,__new:!0},this.dirty=!0,this.test=null,this.models=[]},async save(){let e=this.cur;if(e){if(!String(e.label||"").trim()){D("\u7ED9\u63D0\u4F9B\u5546\u8D77\u4E2A\u540D\u5B57","err");return}if(!String(e.api_base||"").trim()){D("api_base \u4E0D\u80FD\u4E3A\u7A7A","err");return}this.busy="save";try{await Ue("rcbot.provider.save",{id:e.__new?"":e.id,label:e.label,type:e.type,api_base:e.api_base,api_key:e.api_key,model:e.model,timeout:Number(e.timeout)||120,enable:!!e.enable}),D("\u5DF2\u4FDD\u5B58","ok"),this.dirty=!1,this.cur=null,await this.load()}catch(t){D(Z(t),"err")}finally{this.busy=""}}},async setDefault(e){this.busy="def"+e.id;try{await Ue("rcbot.provider.save",{id:e.id,label:e.label,type:e.type,api_base:e.api_base,api_key:e.api_key,model:e.model,timeout:e.timeout,enable:e.enable,set_default:!0}),D("\u5DF2\u8BBE\u4E3A\u9ED8\u8BA4\u63D0\u4F9B\u5546","ok"),await this.load()}catch(t){D(Z(t),"err")}finally{this.busy=""}},async del(e){if(confirm("\u5220\u9664\u63D0\u4F9B\u5546\u300C"+(e.label||e.id)+"\u300D\uFF1F")){this.busy="del"+e.id;try{await Ue("rcbot.provider.delete",{id:e.id}),D("\u5DF2\u5220\u9664","ok"),this.cur=null,await this.load()}catch(t){D(Z(t),"err")}finally{this.busy=""}}},async doTest(e){this.busy="test"+e.id,this.test=null;try{let t=await Y("rcbot.provider.test",{id:e.id});this.test=Object.assign({id:e.id},t||{}),D(t.ok?"\u901A\u4E86\uFF0C"+t.ms+"ms":"\u4E0D\u901A\uFF1A"+(t.error||""),t.ok?"ok":"err")}catch(t){D(Z(t),"err")}finally{this.busy=""}},async fetchModels(){let e=this.cur;if(!e||e.__new){D("\u5148\u4FDD\u5B58\u518D\u62C9\u6A21\u578B\u5217\u8868","err");return}this.busy="models";try{let t=await Y("rcbot.provider.models",{id:e.id});this.models=t&&(t.items||t.models)||[],this.models.length||D("\u6CA1\u62C9\u5230\u6A21\u578B","err")}catch(t){D(Z(t),"err")}finally{this.busy=""}}},template:`
  <div class="rcq-split">
    <div class="rcq-pnl flat">
      <div class="rcq-ph" style="padding:14px 16px 0;margin-bottom:10px">
        <b>\u6A21\u578B\u63D0\u4F9B\u5546</b><span class="sp"></span>
        <button class="btn btn-sm btn-primary" @click="add">\u65B0\u589E</button>
      </div>
      <div class="rcq-list">
        <div class="rcq-row click" v-for="p in list" :key="p.id"
          :class="{ on: cur && cur.id === p.id }" @click="pick(p)">
          <div class="main">
            <div class="t">{{ p.label || p.id }}
              <span class="tag-chip tag-chip-sm" v-if="p.id === def">\u9ED8\u8BA4</span>
              <span class="tag-chip tag-chip-sm" v-if="p.enable === false">\u505C\u7528</span>
            </div>
            <div class="d">{{ p.model || '\u672A\u9009\u6A21\u578B' }} \xB7 {{ p.api_base }}</div>
          </div>
        </div>
        <div v-if="!list.length" class="rcq-empty"><b>\u2726</b>\u8FD8\u6CA1\u6709\u63D0\u4F9B\u5546\uFF0C\u70B9\u300C\u65B0\u589E\u300D</div>
      </div>
    </div>

    <div class="rcq-pnl" v-if="cur">
      <div class="rcq-ph"><b>{{ isNew ? '\u65B0\u589E\u63D0\u4F9B\u5546' : (cur.label || cur.id) }}</b><span class="sp"></span>
        <span class="tag-chip tag-chip-sm" v-if="cur.id && cur.id === def">\u9ED8\u8BA4</span>
      </div>
      <div class="rcq-form">
        <label class="rcq-fi"><span>\u540D\u79F0</span>
          <input class="input" v-model="cur.label" @input="dirty = true" placeholder="DeepSeek" /></label>
        <label class="rcq-fi"><span>\u534F\u8BAE</span>
          <select class="select" v-model="cur.type" @change="dirty = true">
            <option value="openai">OpenAI \u517C\u5BB9</option>
            <option value="anthropic">Anthropic</option>
          </select></label>
        <label class="rcq-fi wide"><span>API \u5730\u5740</span>
          <input class="input" v-model="cur.api_base" @input="dirty = true"
            placeholder="https://api.deepseek.com/v1" /></label>
        <label class="rcq-fi wide"><span>API Key</span>
          <div style="display:flex;gap:6px">
            <input class="input" style="flex:1" v-model="cur.api_key" @input="dirty = true"
              :type="showKey ? 'text' : 'password'" placeholder="sk-..." />
            <button class="btn btn-sm" @click="showKey = !showKey">{{ showKey ? '\u9690\u85CF' : '\u663E\u793A' }}</button>
          </div>
        </label>
        <label class="rcq-fi"><span>\u6A21\u578B</span>
          <div style="display:flex;gap:6px">
            <input class="input" style="flex:1" v-model="cur.model" @input="dirty = true"
              placeholder="deepseek-flash" />
            <button class="btn btn-sm" :disabled="!!busy || isNew" @click="fetchModels">\u62C9\u5217\u8868</button>
          </div>
        </label>
        <label class="rcq-fi"><span>\u8D85\u65F6\uFF08\u79D2\uFF09</span>
          <input class="input" type="number" min="10" max="600" v-model="cur.timeout" @input="dirty = true" /></label>
        <div class="rcq-fi" v-if="models.length"><span>\u4ECE\u5217\u8868\u9009\uFF08{{ models.length }}\uFF09</span>
          <select class="select" :value="cur.model" @change="cur.model = $event.target.value; dirty = true">
            <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
      </div>

      <div class="rcq-flex" style="margin-top:12px">
        <button class="btn btn-primary btn-sm" :disabled="!!busy" @click="save">\u4FDD\u5B58</button>
        <button class="btn btn-sm" v-if="cur.id && cur.id !== def" :disabled="!!busy"
          @click="setDefault(cur)">\u8BBE\u4E3A\u9ED8\u8BA4</button>
        <button class="btn btn-sm" v-if="cur.id && !isNew" :disabled="!!busy" @click="doTest(cur)">\u6D4B\u8BD5\u8FDE\u901A</button>
        <button class="btn btn-sm btn-danger" v-if="cur.id && !isNew" :disabled="!!busy"
          @click="del(cur)">\u5220\u9664</button>
        <span class="rcq-hint" v-if="dirty">\u6709\u672A\u4FDD\u5B58\u7684\u4FEE\u6539</span>
      </div>
      <div class="rcq-note" v-if="test">
        <span :style="{ color: test.ok ? 'var(--success)' : 'var(--danger)' }">
          {{ test.ok ? ('\u8FDE\u901A ' + test.ms + 'ms \xB7 \u56DE\u590D\uFF1A' + (test.reply || '')) : ('\u5931\u8D25\uFF1A' + (test.error || '')) }}
        </span>
      </div>
      <div class="rcq-note">
        \u63A8\u7406\u6A21\u578B\uFF08deepseek-flash \u7B49\uFF09\u4F1A\u5148\u82B1 token \u5728\u601D\u8003\u4E0A\uFF0C\u6D4B\u8FDE\u901A\u81F3\u5C11\u7ED9 256 \u4E2A\u8F93\u51FA token\uFF0C
        \u6240\u4EE5\u300C\u6D4B\u8BD5\u8FDE\u901A\u300D\u5076\u5C14\u6162\u4E00\u70B9\u662F\u6B63\u5E38\u7684\u3002
      </div>
    </div>

    <div class="rcq-pnl" v-else>
      <div class="rcq-empty"><b>\u2726</b>\u5DE6\u8FB9\u9009\u4E00\u4E2A\uFF0C\u6216\u8005\u65B0\u589E</div>
    </div>
  </div>`},$m={data(){return{S:yt,items:[],mode:"live",level:"",lines:400,follow:!0,source:"",connected:!1,hint:"",busy:!1,timer:null,err:"",stats:null}},computed:{filtered(){return this.items}},async mounted(){await this.load(),await this.loadStats(),this.tick()},beforeUnmount(){this.timer&&clearTimeout(this.timer)},methods:{tick(){this.timer&&clearTimeout(this.timer),this.mode==="live"&&this.follow&&(this.timer=setTimeout(async()=>{await this.load(!0),await this.loadStats(!0),this.tick()},2e3))},async loadStats(e){try{this.stats=await Y("qqbot.tools.stats",{})}catch(t){e||(this.err=Z(t))}},async load(e){e||(this.busy=!0);try{let t=await Ue("qqbot.account.logs",{mode:this.mode,level:this.level,lines:Number(this.lines)||400}),i=t.items.length!==this.items.length;this.items=t.items||[],this.source=t.source,this.connected=!!t.connected,this.hint=t.hint||"",this.err="",i&&this.follow&&this.$nextTick(this.scrollBottom)}catch(t){this.err=Z(t)}finally{this.busy=!1}},scrollBottom(){let e=this.$refs.box;e&&(e.scrollTop=e.scrollHeight)},async switchMode(e){this.mode=e,this.items=[],await this.load(),this.tick()},async setLevel(e){this.level=this.level===e?"":e,await this.load()},async clear(){try{await Ue("qqbot.account.logs.clear"),this.items=[],D("\u5DF2\u6E05\u7A7A\u5F53\u524D\u89C6\u56FE\uFF08\u5BB9\u5668\u65E5\u5FD7\u7531 Docker \u7BA1\u7406\uFF09","ok")}catch(e){D(Z(e),"err")}},download(){let e=this.items.map(s=>"["+String(s.level).toUpperCase()+"] "+s.text).join(`
`),t=new Blob([e],{type:"text/plain;charset=utf-8"}),i=document.createElement("a");i.href=URL.createObjectURL(t),i.download="snowluma-"+Date.now()+".log",i.click(),setTimeout(()=>URL.revokeObjectURL(i.href),3e3)},lineClass(e){return"rcq-ln rcq-lv-"+(e.level||"info")},lvText(e){return"["+String(e.level||"info").toUpperCase()+"]"}},template:`
  <div>
    <div class="rcq-pnl">
      <div class="rcq-ph">
        <button class="btn btn-sm" :class="mode === 'live' ? 'btn-primary' : ''" @click="switchMode('live')">\u5B9E\u65F6\u65E5\u5FD7</button>
        <button class="btn btn-sm" :class="mode === 'history' ? 'btn-primary' : ''" @click="switchMode('history')">\u5386\u53F2\u65E5\u5FD7</button>
        <span class="sp"></span>
        <span class="rcq-lamp"><b :class="connected ? 'on' : 'off'"></b>
          {{ connected ? '\u5BB9\u5668\u5728\u7EBF' : '\u5BB9\u5668\u79BB\u7EBF' }} \xB7 docker logs</span>
      </div>
      <div class="rcq-flex">
        <span class="rcq-hint">\u65E5\u5FD7\u7EA7\u522B</span>
        <button class="btn btn-sm" :class="level === 'debug' ? 'btn-primary' : ''" @click="setLevel('debug')">Debug</button>
        <button class="btn btn-sm" :class="level === 'info' ? 'btn-primary' : ''" @click="setLevel('info')">Info</button>
        <button class="btn btn-sm" :class="level === 'warn' ? 'btn-primary' : ''" @click="setLevel('warn')">Warn</button>
        <button class="btn btn-sm" :class="level === 'error' ? 'btn-primary' : ''" @click="setLevel('error')">Error</button>
        <span style="width:10px"></span>
        <select class="select" style="padding:4px 8px;font-size:12px" v-model.number="lines" @change="load()">
          <option :value="200">200 \u884C</option>
          <option :value="400">400 \u884C</option>
          <option :value="1000">1000 \u884C</option>
          <option :value="2000">2000 \u884C</option>
        </select>
        <label class="switch" title="\u81EA\u52A8\u8DDF\u968F">
          <input type="checkbox" v-model="follow" @change="tick" />
          <span class="slider"></span>
        </label>
        <span class="rcq-hint">\u8DDF\u968F</span>
        <span class="sp" style="margin-left:auto"></span>
        <button class="btn btn-sm" :disabled="busy" @click="load()">\u5237\u65B0</button>
        <button class="btn btn-sm" @click="download">\u4E0B\u8F7D</button>
        <button class="btn btn-sm" v-if="mode === 'live'" @click="clear">\u6E05\u7A7A</button>
      </div>
    </div>

    <div class="rcq-pnl">
      <div class="rcq-flex">
        <b>\u5DE5\u5177\u8C03\u7528\u7EDF\u8BA1</b>
        <span class="rcq-hint">\u672C\u6B21\u8FDB\u7A0B\u8FD0\u884C\u4EE5\u6765\uFF08AI \u8C03\u7528 + \u624B\u52A8\u6D4B\u8BD5\uFF09</span>
        <span style="margin-left:auto"></span>
        <button class="btn btn-sm" @click="loadStats()">\u5237\u65B0</button>
      </div>
      <div v-if="stats" class="rcq-flex" style="gap:18px;margin-top:8px;flex-wrap:wrap">
        <span class="rcq-hint">\u603B\u8C03\u7528 <b>{{ stats.total }}</b></span>
        <span class="rcq-hint">\u6210\u529F <b style="color:var(--ok,#5fd38d)">{{ stats.ok }}</b></span>
        <span class="rcq-hint">\u5931\u8D25 <b style="color:var(--bad,#e0533f)">{{ stats.fail }}</b></span>
        <span class="rcq-hint">\u6210\u529F\u7387 <b>{{ stats.rate }}%</b></span>
      </div>
      <div v-if="stats && stats.tools.length" style="margin-top:8px">
        <div v-for="t in stats.tools" :key="t.id" class="rcq-flex"
          style="padding:7px 0;border-bottom:1px solid var(--bd)">
          <b style="min-width:110px">{{ t.name }}</b>
          <span class="rcq-hint">\u8C03\u7528 {{ t.calls }}</span>
          <span class="rcq-hint" style="margin-left:10px">\u6210\u529F {{ t.ok }}</span>
          <span class="rcq-hint" style="margin-left:10px">\u5931\u8D25 {{ t.fail }}</span>
          <span class="rcq-hint" style="margin-left:auto">\u5E73\u5747 {{ t.avg_ms }}ms</span>
        </div>
      </div>
      <div v-else class="rcq-hint" style="margin-top:8px">\u8FD8\u6CA1\u6709\u5DE5\u5177\u8C03\u7528</div>
      <div v-if="stats && stats.recent.length" style="margin-top:10px">
        <div class="rcq-hint" style="margin-bottom:4px">\u6700\u8FD1\u8C03\u7528</div>
        <div v-for="(r, i) in stats.recent" :key="i" class="rcq-flex"
          style="font-size:12px;padding:3px 0;border-bottom:1px dashed var(--bd)">
          <span class="mono" style="color:var(--m)">{{ r.time }}</span>
          <span style="margin-left:8px">{{ r.name }}</span>
          <span class="rcq-hint" style="margin-left:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:320px">{{ r.args }}</span>
          <span :style="{ marginLeft: 'auto', color: r.ok ? 'var(--ok,#5fd38d)' : 'var(--bad,#e0533f)' }">
            {{ r.ok ? 'ok' : 'fail' }} \xB7 {{ r.ms }}ms</span>
        </div>
      </div>
    </div>

    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-log" ref="box">
      <div v-for="(x, i) in items" :key="i" :class="lineClass(x)">
        <span class="lv">{{ lvText(x) }}</span>{{ x.text }}
      </div>
      <div v-if="!items.length" style="color:var(--f)">
        {{ hint || '\u8FD8\u6CA1\u6709\u65E5\u5FD7' }}
      </div>
    </div>
    <div class="rcq-note">
      \u65E5\u5FD7\u6765\u81EA <code>docker logs snowluma</code>\uFF08\u5BB9\u5668\u65E5\u5FD7\u672C\u8EAB\u5E26\u5386\u53F2\uFF0C\u6BCF 2 \u79D2\u5237\u65B0\u4E00\u6B21\uFF09\u3002
      \u5BB9\u5668\u6CA1\u8D77\u6765\u65F6\u8FD9\u91CC\u4F1A\u662F\u7A7A\u7684\u3002
    </div>
  </div>`},Um={data(){return{S:yt,cfg:null,conn:null,busy:"",err:"",searchQ:"",searchOut:null,tab:"ctx"}},computed:{ctx(){return this.cfg&&this.cfg.context||{}},bot(){return this.cfg&&this.cfg.bot||{}},feats(){return this.cfg&&this.cfg.features||{}},ws(){return this.feats.web_search||{}},vis(){return this.feats.vision||{}},rp(){return this.feats.random_pick||{}},sl(){return this.feats.sl_status||{}},ai(){return this.cfg?(this.cfg.features=this.cfg.features||{},this.cfg.features.ai=this.cfg.features.ai||{enabled:!0},this.cfg.features.ai):{enabled:!0}},pnl(){return this.cfg?(this.cfg.features=this.cfg.features||{},this.cfg.features.panel=this.cfg.features.panel||{enabled:!0},this.cfg.features.panel):{enabled:!0}}},async mounted(){await this.load()},methods:{async load(){this.busy="load";try{this.cfg=await Y("rcbot.config.get"),this.conn=await Ue("qqbot.conn.get"),this.err=""}catch(e){this.err=Z(e)}finally{this.busy=""}},async saveCtx(){this.busy="ctx";try{await Ue("rcbot.config.save",{context:{max_tokens:Number(this.ctx.max_tokens)||128e3,max_output_tokens:Number(this.ctx.max_output_tokens)||4096,keep_recent_ratio:Number(this.ctx.keep_recent_ratio)||.15,max_history_messages:Number(this.ctx.max_history_messages)||200,compress_enabled:!!this.ctx.compress_enabled,compress_provider:this.ctx.compress_provider||""}}),D("\u4E0A\u4E0B\u6587\u8BBE\u7F6E\u5DF2\u4FDD\u5B58","ok"),await this.load()}catch(e){D(Z(e),"err")}finally{this.busy=""}},async saveBot(){this.busy="bot";try{await Ue("rcbot.config.save",{bot:{enabled:!!this.bot.enabled,group_need_at:!!this.bot.group_need_at,private_always_reply:!!this.bot.private_always_reply,reply_with_mention:!!this.bot.reply_with_mention,reply_with_quote:this.bot.reply_with_quote!==!1,reply_when_quoted:this.bot.reply_when_quoted!==!1,wake_prefix:fl(this.bot.__prefixText!=null?this.bot.__prefixText:(this.bot.wake_prefix||[]).join(",")),allowed_groups:fl(this.bot.__allowText!=null?this.bot.__allowText:(this.bot.allowed_groups||[]).join(",")),blocked_groups:fl(this.bot.__blockText!=null?this.bot.__blockText:(this.bot.blocked_groups||[]).join(",")),rate_limit:{window:Number((this.bot.rate_limit||{}).window)||60,max:Number((this.bot.rate_limit||{}).max)||30}}}),D("\u89E6\u53D1\u89C4\u5219\u5DF2\u4FDD\u5B58","ok"),await this.load()}catch(e){D(Z(e),"err")}finally{this.busy=""}},async saveFeat(){this.busy="feat";try{await Ue("rcbot.config.save",{features:{ai:{enabled:!!this.ai.enabled},panel:{enabled:!!this.pnl.enabled},web_search:{enabled:!!this.ws.enabled,max_results:Number(this.ws.max_results)||5},vision:{enabled:!!this.vis.enabled,max_images:Number(this.vis.max_images)||3},random_pick:{enabled:this.rp.enabled!==!1,scope:this.rp.scope||"enabled_groups",respect_need_at:!!this.rp.respect_need_at},sl_status:{enabled:this.sl.enabled!==!1,keyword:String(this.sl.keyword||"#sl").trim()||"#sl",cooldown:Math.max(1,Number(this.sl.cooldown)||10)}}}),D("\u80FD\u529B\u5F00\u5173\u5DF2\u4FDD\u5B58","ok"),await this.load()}catch(e){D(Z(e),"err")}finally{this.busy=""}},async saveConn(){this.busy="conn";try{await Ue("qqbot.conn.save",{config:{api:this.conn.config.api,timeout:Number(this.conn.config.timeout)||90}}),D("\u8FDE\u63A5\u8BBE\u7F6E\u5DF2\u4FDD\u5B58","ok"),await this.load()}catch(e){D(Z(e),"err")}finally{this.busy=""}},async testSearch(){let e=this.searchQ.trim();if(e){this.busy="search",this.searchOut=null;try{let t=await Y("rcbot.tools.search",{q:e});this.searchOut=t||{}}catch(t){D(Z(t),"err")}finally{this.busy=""}}}},template:`
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>
    <div class="rcq-pnl" v-if="!cfg"><div class="rcq-empty">\u8BFB\u53D6\u914D\u7F6E\u4E2D\u2026</div></div>

    <div class="rcq-pnl" v-if="cfg">
      <div class="rcq-ph">
        <button class="btn btn-sm" :class="tab === 'ctx' ? 'btn-primary' : ''" @click="tab = 'ctx'">\u4E0A\u4E0B\u6587\u4E0E\u89E6\u53D1</button>
        <button class="btn btn-sm" :class="tab === 'cap' ? 'btn-primary' : ''" @click="tab = 'cap'">\u80FD\u529B</button>
        <button class="btn btn-sm" :class="tab === 'conn' ? 'btn-primary' : ''" @click="tab = 'conn'">\u8FDE\u63A5</button>
        <span class="sp"></span>
        <button class="btn btn-sm" :disabled="!!busy" @click="load">\u91CD\u65B0\u8BFB\u53D6</button>
      </div>

      <!-- \u4E0A\u4E0B\u6587\u4E0E\u89E6\u53D1 -->
      <div v-if="tab === 'ctx'">
        <div class="rcq-ph" style="margin-bottom:10px"><b>\u4E0A\u4E0B\u6587</b>
          <span class="rcq-hint">\u51B3\u5B9A\u5B83\u8BB0\u5F97\u591A\u5C11\u3001\u4EC0\u4E48\u65F6\u5019\u538B\u7F29</span></div>
        <div class="rcq-form">
          <label class="rcq-fi"><span>\u6A21\u578B\u4E0A\u4E0B\u6587\u7A97\u53E3\uFF08tokens\uFF09</span>
            <input class="input" type="number" v-model="ctx.max_tokens" /></label>
          <label class="rcq-fi"><span>\u6700\u5927\u8F93\u51FA\uFF08tokens\uFF09</span>
            <input class="input" type="number" v-model="ctx.max_output_tokens" /></label>
          <label class="rcq-fi"><span>\u4FDD\u7559\u6700\u8FD1\u6BD4\u4F8B</span>
            <input class="input" type="number" step="0.05" min="0.05" max="0.9" v-model="ctx.keep_recent_ratio" /></label>
          <label class="rcq-fi"><span>\u6700\u591A\u5E26\u591A\u5C11\u6761\u5386\u53F2</span>
            <input class="input" type="number" v-model="ctx.max_history_messages" /></label>
        </div>
        <div class="switch-row">
          <label>\u542F\u7528\u4E0A\u4E0B\u6587\u538B\u7F29\uFF08\u8D85\u9884\u7B97\u65F6\u628A\u65E7\u5BF9\u8BDD\u538B\u6210\u6458\u8981\uFF09</label>
          <label class="switch"><input type="checkbox" v-model="ctx.compress_enabled" /><span class="slider"></span></label>
        </div>
        <div class="rcq-note">
          \u9884\u7B97 = \u4E0A\u4E0B\u6587\u7A97\u53E3 \u2212 \u6700\u5927\u8F93\u51FA \u2212 \u7CFB\u7EDF\u63D0\u793A\u3002\u8D85\u4E86\u5C31\u4FDD\u7559\u6700\u8FD1 {{ Math.round((ctx.keep_recent_ratio || 0) * 100) }}%\uFF0C
          \u66F4\u65E7\u7684\u4EA4\u7ED9\u6A21\u578B\u538B\u6210\u6458\u8981\u3002\u63A8\u7406\u6A21\u578B\u5EFA\u8BAE\u300C\u6700\u5927\u8F93\u51FA\u300D\u2265 4096\uFF0C\u5426\u5219\u601D\u8003\u5C31\u628A\u9884\u7B97\u5403\u5149\u4E86\u3002
        </div>
        <div class="rcq-flex" style="margin-top:12px">
          <button class="btn btn-primary btn-sm" :disabled="!!busy" @click="saveCtx">\u4FDD\u5B58</button>
        </div>

        <div class="rcq-sec">
          <div class="rcq-ph" style="margin-bottom:10px"><b>\u89E6\u53D1\u89C4\u5219</b>
            <span class="rcq-hint">\u4EC0\u4E48\u6D88\u606F\u624D\u56DE</span></div>
          <div class="switch-row">
            <label>\u673A\u5668\u4EBA\u603B\u5F00\u5173</label>
            <label class="switch"><input type="checkbox" v-model="bot.enabled" /><span class="slider"></span></label>
          </div>
          <div class="switch-row">
            <label>\u7FA4\u91CC\u5FC5\u987B @ \u624D\u56DE\u590D</label>
            <label class="switch"><input type="checkbox" v-model="bot.group_need_at" /><span class="slider"></span></label>
          </div>
          <div class="switch-row">
            <label>\u79C1\u804A\u5168\u90E8\u56DE\u590D</label>
            <label class="switch"><input type="checkbox" v-model="bot.private_always_reply" /><span class="slider"></span></label>
          </div>
          <div class="switch-row">
            <label>\u56DE\u590D\u65F6 @ \u5BF9\u65B9</label>
            <label class="switch"><input type="checkbox" v-model="bot.reply_with_mention" /><span class="slider"></span></label>
          </div>
          <div class="switch-row">
            <label>\u56DE\u590D\u65F6\u5F15\u7528\u539F\u6D88\u606F</label>
            <label class="switch"><input type="checkbox" v-model="bot.reply_with_quote" /><span class="slider"></span></label>
          </div>
          <div class="switch-row">
            <label>\u5F15\u7528\u673A\u5668\u4EBA\u6D88\u606F\u65F6\u56DE\u590D
              <div class="rcq-note">\u7FA4\u91CC\u6CA1 @ \u4F46\u5F15\u7528\u4E86\u673A\u5668\u4EBA\u8BF4\u7684\u8BDD\uFF0C\u4E5F\u7B97\u5728\u8DDF\u5B83\u8BF4\u8BDD\u3002</div>
            </label>
            <label class="switch"><input type="checkbox" v-model="bot.reply_when_quoted" /><span class="slider"></span></label>
          </div>
          <div class="rcq-form" style="margin-top:8px">
            <label class="rcq-fi"><span>\u5524\u9192\u524D\u7F00\uFF08\u9017\u53F7\u5206\u9694\uFF0C\u4E0D\u7528 @\uFF09</span>
              <input class="input" :value="(bot.wake_prefix || []).join(',')"
                @input="bot.__prefixText = $event.target.value" placeholder="/" /></label>
            <label class="rcq-fi"><span>\u9650\u6D41\uFF1A\u7A97\u53E3\uFF08\u79D2\uFF09</span>
              <input class="input" type="number" v-model="bot.rate_limit.window" /></label>
            <label class="rcq-fi"><span>\u9650\u6D41\uFF1A\u7A97\u53E3\u5185\u6700\u591A\u56DE\u590D</span>
              <input class="input" type="number" v-model="bot.rate_limit.max" /></label>
            <label class="rcq-fi"><span>\u53EA\u56DE\u8FD9\u4E9B\u7FA4\uFF08\u7559\u7A7A = \u4E0D\u9650\uFF09</span>
              <input class="input" :value="(bot.allowed_groups || []).join(',')"
                @input="bot.__allowText = $event.target.value" placeholder="\u7FA4\u53F7\uFF0C\u9017\u53F7\u5206\u9694" /></label>
            <label class="rcq-fi"><span>\u5C4F\u853D\u8FD9\u4E9B\u7FA4</span>
              <input class="input" :value="(bot.blocked_groups || []).join(',')"
                @input="bot.__blockText = $event.target.value" placeholder="\u7FA4\u53F7\uFF0C\u9017\u53F7\u5206\u9694" /></label>
          </div>
          <div class="rcq-flex" style="margin-top:12px">
            <button class="btn btn-primary btn-sm" :disabled="!!busy" @click="saveBot">\u4FDD\u5B58</button>
          </div>
        </div>
      </div>

      <!-- \u80FD\u529B -->
      <div v-if="tab === 'cap'">
        <div class="switch-row">
          <label>AI \u56DE\u590D
            <div class="rcq-note">\u5173\u95ED\u540E\u666E\u901A\u6D88\u606F\u4E0D\u8C03\u7528\u6A21\u578B\uFF1B\u9762\u677F\u83DC\u5355\u4E0E\u529F\u80FD\u4ECD\u53EF\u7528\u3002</div>
          </label>
          <label class="switch"><input type="checkbox" v-model="ai.enabled" /><span class="slider"></span></label>
        </div>
        <div class="switch-row">
          <label>\u83DC\u5355\u9762\u677F
            <div class="rcq-note">\u5173\u95ED\u540E @\u673A\u5668\u4EBA \u83DC\u5355 \u4EA4\u7ED9 AI \u5904\u7406\u3002</div>
          </label>
          <label class="switch"><input type="checkbox" v-model="pnl.enabled" /><span class="slider"></span></label>
        </div>
        <div class="switch-row">
          <label>\u5141\u8BB8\u8054\u7F51\u641C\u7D22
            <div class="rcq-note">\u6A21\u578B\u9047\u5230\u65F6\u6548\u6027\u95EE\u9898\u4F1A\u8C03\u7528 <code>web_search</code>\uFF0C\u8D70 Bing \u6293\u7ED3\u679C\u3002</div>
          </label>
          <label class="switch"><input type="checkbox" v-model="ws.enabled" /><span class="slider"></span></label>
        </div>
        <div class="rcq-form" style="margin-top:6px">
          <label class="rcq-fi"><span>\u6BCF\u6B21\u641C\u7D22\u53D6\u51E0\u6761</span>
            <input class="input rcq-num" type="number" min="1" max="10" v-model="ws.max_results" /></label>
        </div>

        <div class="rcq-sec">
          <div class="switch-row">
            <label>\u5141\u8BB8\u8BC6\u56FE
              <div class="rcq-note">\u6D88\u606F\u91CC\u6709\u56FE\u7247\u65F6\uFF0C\u628A\u56FE\u8F6C\u6210 base64 \u76F4\u63A5\u5582\u7ED9\u6A21\u578B\uFF08\u4E0D\u7528\u53E6\u914D\u89C6\u89C9\u6A21\u578B\uFF09\u3002</div>
            </label>
            <label class="switch"><input type="checkbox" v-model="vis.enabled" /><span class="slider"></span></label>
          </div>
          <div class="rcq-form" style="margin-top:6px">
            <label class="rcq-fi"><span>\u5355\u6761\u6D88\u606F\u6700\u591A\u770B\u51E0\u5F20</span>
              <input class="input rcq-num" type="number" min="1" max="6" v-model="vis.max_images" /></label>
          </div>
<div class="rcq-note">
          \u53EA\u6709\u300C\u5F53\u524D\u8FD9\u8F6E\u300D\u4F1A\u5E26\u56FE\uFF0C\u5386\u53F2\u91CC\u53EA\u7559 [\u56FE\u7247] \u6587\u672C \u2014\u2014 \u4E0D\u7136\u6BCF\u8F6E\u90FD\u8981\u91CD\u4F20\u56FE\u7247\uFF0Ctoken \u4F1A\u7206\u3002
          </div>
        </div>

        <div class="rcq-sec">
          <div class="switch-row">
            <label>\u5141\u8BB8\u968F\u673A\u6311\u6D88\u606F\u56DE
              <div class="rcq-note">
                \u6D88\u606F\u9875\u7684 \u{1F3B2}\uFF1A\u4ECE\u7FA4\u804A\u91CC\u968F\u673A\u7FFB\u4E00\u6761\u522B\u4EBA\u8BF4\u8FC7\u7684\u8BDD\uFF0C\u8BA9\u673A\u5668\u4EBA\u5BF9\u5B83\u56DE\u4E00\u53E5\u3002
                \u70B9\u300C\u53D1\u9001\u5230 QQ\u300D\u4F1A\u771F\u7684\u53D1\u5230\u90A3\u4E2A\u7FA4\u91CC\uFF08\u5E76 @ \u539F\u8BF4\u8BDD\u4EBA\uFF09\u3002
              </div>
            </label>
            <label class="switch"><input type="checkbox" v-model="rp.enabled" /><span class="slider"></span></label>
          </div>
          <div class="rcq-form" style="margin-top:6px">
            <label class="rcq-fi"><span>\u4ECE\u54EA\u91CC\u6311</span>
              <select class="input" v-model="rp.scope">
                <option value="enabled_groups">\u5DF2\u542F\u7528\u7684\u7FA4\u804A\uFF08\u63A8\u8350\uFF09</option>
                <option value="all_groups">\u6240\u6709\u7FA4\u804A</option>
              </select>
            </label>
          </div>
          <div class="switch-row">
            <label>\u968F\u673A\u6311\u4E5F\u9075\u5B88\u300C\u7FA4\u91CC\u5FC5\u987B @\u300D
              <div class="rcq-note">
                \u5F00\u542F\u540E\u53EA\u6311 @\u8FC7\u673A\u5668\u4EBA\uFF08\u6216\u5E26\u5524\u9192\u524D\u7F00\uFF09\u7684\u6D88\u606F\uFF0C\u907F\u514D\u548C\u300C\u7FA4\u91CC\u5FC5\u987B @ \u624D\u56DE\u590D\u300D\u51B2\u7A81\uFF1B
                \u5173\u95ED = \u968F\u673A\u6311\u662F\u624B\u52A8\u89E6\u53D1\uFF0C\u4E0D\u53D7\u8FD9\u6761\u89C4\u5219\u9650\u5236\u3002
              </div>
            </label>
            <label class="switch"><input type="checkbox" v-model="rp.respect_need_at" /><span class="slider"></span></label>
          </div>
          <div class="rcq-note">
            \u300C\u5DF2\u542F\u7528\u7684\u7FA4\u804A\u300D= \u5728\u300C\u4F1A\u8BDD\u7BA1\u7406\u300D\u91CC\u6253\u5F00\u5F00\u5173\u7684\u90A3\u4E9B\u7FA4\u3002\u8FD8\u6CA1\u542F\u7528\u7684\u7FA4\u4E0D\u53C2\u4E0E\u6311\u9009\u3002
            \u6311\u9009\u4E0D\u662F\u7EAF\u968F\u673A\uFF1A\u6309\u300C\u957F\u5EA6\u5408\u9002\u3001\u50CF\u5728\u95EE\u8BDD\u3001\u6BD4\u8F83\u65B0\u3001\u5404\u7FA4\u8F6E\u6362\u300D\u52A0\u6743\uFF0C\u907F\u514D\u7FFB\u5230
            <code>[\u56FE\u7247]</code>\u3001\u5355\u5B57\u56DE\u590D\u6216\u53CD\u590D\u540C\u4E00\u7FA4\u3002
          </div>
        </div>

        <div class="rcq-sec">
          <div class="switch-row">
            <label>\u5141\u8BB8 #sl \u72B6\u6001\u6307\u4EE4
              <div class="rcq-note">
                \u4EFB\u610F\u7FA4\u804A / \u79C1\u804A\u91CC\u53D1 <b>#sl</b>\uFF0C\u673A\u5668\u4EBA\u56DE\u4E00\u6761 SnowLuma \u72B6\u6001
                \uFF08\u5BB9\u5668\u3001QQ \u767B\u5F55\u3001OneBot \u8FDE\u63A5\u3001\u6D88\u606F\u6863\u6848\u6761\u6570\uFF09\u3002
                \u5173\u6389\u540E #sl \u53EA\u662F\u666E\u901A\u6D88\u606F\uFF0C\u8D70\u6B63\u5E38\u7684 @ / \u5524\u9192\u89C4\u5219\u3002
              </div>
            </label>
            <label class="switch"><input type="checkbox" v-model="sl.enabled" /><span class="slider"></span></label>
          </div>
          <div class="rcq-form" style="margin-top:6px">
            <label class="rcq-fi"><span>\u89E6\u53D1\u5173\u952E\u8BCD</span>
              <input class="input" v-model="sl.keyword" placeholder="#sl" /></label>
            <label class="rcq-fi"><span>\u51B7\u5374\uFF08\u79D2\uFF09</span>
              <input class="input rcq-num" type="number" min="1" max="600" v-model="sl.cooldown" /></label>
          </div>
          <div class="rcq-note">\u540C\u4E00\u4F1A\u8BDD\u5728\u51B7\u5374\u65F6\u95F4\u5185\u53EA\u56DE\u4E00\u6B21\uFF0C\u907F\u514D\u7FA4\u91CC\u5237\u5C4F\u3002</div>
        </div>

        <div class="rcq-flex" style="margin-top:12px">
          <button class="btn btn-primary btn-sm" :disabled="!!busy" @click="saveFeat">\u4FDD\u5B58</button>
        </div>

        <div class="rcq-sec">
          <div class="rcq-ph" style="margin-bottom:10px"><b>\u8BD5\u4E00\u4E0B\u641C\u7D22</b>
            <span class="rcq-hint">\u9A8C\u8BC1 Bing \u901A\u9053\u901A\u4E0D\u901A</span></div>
          <div class="rcq-flex">
            <input class="input" style="flex:1;min-width:160px" v-model="searchQ"
              @keyup.enter="testSearch" placeholder="\u4F8B\u5982\uFF1A\u676D\u5DDE\u5929\u6C14" />
            <button class="btn btn-sm" :disabled="busy === 'search'" @click="testSearch">\u641C\u7D22</button>
          </div>
          <div v-if="searchOut" style="margin-top:10px">
            <div class="rcq-list">
              <div class="rcq-row" v-for="(r, i) in (searchOut.results || [])" :key="i">
                <div class="main">
                  <div class="t">{{ r.title }}</div>
                  <div class="d" style="white-space:normal">{{ r.snippet }}</div>
                  <div class="d rcq-mono">{{ r.url }}</div>
                </div>
              </div>
              <div v-if="!(searchOut.results || []).length" class="rcq-empty">\u6CA1\u6709\u7ED3\u679C</div>
            </div>
          </div>
        </div>
      </div>

      <!-- \u8FDE\u63A5 -->
      <div v-if="tab === 'conn' && conn">
        <div class="rcq-ph" style="margin-bottom:10px"><b>SnowLuma\uFF08\u534F\u8BAE\u7AEF\uFF09</b><span class="sp"></span>
          <span class="rcq-lamp"><b :class="conn.snowluma && conn.snowluma.ok ? 'on' : 'off'"></b>
            {{ conn.snowluma && conn.snowluma.ok ? '\u5BB9\u5668\u5728\u8FD0\u884C' : '\u5BB9\u5668\u672A\u8FD0\u884C' }}</span></div>
        <div class="rcq-note" v-if="conn.snowluma && conn.snowluma.error">{{ conn.snowluma.error }}</div>
        <div class="rcq-note">
          QQ \u8DD1\u5728 Docker \u5BB9\u5668 <code>snowluma</code> \u91CC\uFF08OneBot WS 3001 / HTTP 3000 / noVNC 6081\uFF09\u3002
          \u5BB9\u5668\u6CA1\u8D77\u5C31\u53BB\u300CQQ \u8D26\u6237\u300D\u70B9\u300C\u542F\u52A8\u300D\u6216\u300C\u626B\u7801\u767B\u5F55\u300D\u3002
        </div>

        <div class="rcq-sec">
          <div class="rcq-ph" style="margin-bottom:10px"><b>rcbot\uFF08\u673A\u5668\u4EBA\uFF09</b><span class="sp"></span>
            <span class="rcq-lamp"><b :class="conn.rcbot && conn.rcbot.ok ? 'on' : 'off'"></b>
              {{ conn.rcbot && conn.rcbot.ok ? '\u5DF2\u8FDE\u901A' : '\u8FDE\u4E0D\u4E0A' }}</span></div>
          <div class="rcq-form">
            <label class="rcq-fi wide"><span>HTTP \u5730\u5740</span>
              <input class="input" v-model="conn.config.api" placeholder="http://127.0.0.1:6710" /></label>
            <label class="rcq-fi"><span>\u8BF7\u6C42\u8D85\u65F6\uFF08\u79D2\uFF09</span>
              <input class="input" type="number" v-model="conn.config.timeout" /></label>
          </div>
          <div class="rcq-note" v-if="conn.rcbot && conn.rcbot.error">{{ conn.rcbot.error }}</div>
        </div>

        <div class="rcq-flex" style="margin-top:12px">
          <button class="btn btn-primary btn-sm" :disabled="!!busy" @click="saveConn">\u4FDD\u5B58</button>
          <span class="rcq-hint">\u63D2\u4EF6\u7248\u672C v{{ conn.version }}</span>
        </div>
      </div>
    </div>
  </div>`},Vm={data(){return{loading:!0,busy:"",err:"",tools:[],enabled:{},ws:{root:"",files:0,bytes:0,max_mb:20},fsPath:"",fsItems:[],edit:null,test:null,testOut:""}},async mounted(){await this.load()},methods:{fmtSize(e){return e=Number(e)||0,e>=1048576?(e/1048576).toFixed(1)+" MB":e>=1024?Math.round(e/1024)+" KB":e+" B"},async load(){this.loading=!0;try{let e=await Y("qqbot.tools.get",{});this.tools=e&&e.tools||[],this.enabled=e&&e.enabled||{},this.ws=e&&e.workspace||this.ws,await this.fsList(this.fsPath)}catch(e){this.err=Z(e)}finally{this.loading=!1}},async saveCfg(){this.busy="save";try{await Y("qqbot.tools.save",{enabled:this.enabled,workspace:{max_mb:Number(this.ws.max_mb)||20}}),D("\u5DE5\u5177\u94FE\u8BBE\u7F6E\u5DF2\u4FDD\u5B58","ok")}catch(e){D(Z(e),"err")}finally{this.busy=""}},async fsList(e){try{let t=await Y("qqbot.tools.fs",{action:"list",path:e||""});this.fsPath=t&&t.path||"",this.fsItems=t&&t.items||[]}catch(t){D(Z(t),"err")}},fsGo(e){e.is_dir?this.fsList((this.fsPath?this.fsPath+"/":"")+e.name):this.openFile(e.name)},fsUp(){let e=this.fsPath.split("/").filter(Boolean);e.pop(),this.fsList(e.join("/"))},async openFile(e){let t=(this.fsPath?this.fsPath+"/":"")+e;try{let i=await Y("qqbot.tools.fs",{action:"read",path:t});this.edit={path:t,content:i&&i.content||"",size:i&&i.size||0}}catch(i){D(Z(i),"err")}},newFile(){let e=prompt("\u6587\u4EF6\u540D\uFF08\u53EF\u5E26\u5B50\u76EE\u5F55\uFF0C\u5982 notes/todo.txt\uFF09");e&&(this.edit={path:(this.fsPath?this.fsPath+"/":"")+e,content:"",size:0})},async newDir(){let e=prompt("\u76EE\u5F55\u540D");if(e)try{await Y("qqbot.tools.fs",{action:"mkdir",path:(this.fsPath?this.fsPath+"/":"")+e}),await this.fsList(this.fsPath)}catch(t){D(Z(t),"err")}},async saveFile(){if(this.edit)try{await Y("qqbot.tools.fs",{action:"write",path:this.edit.path,content:this.edit.content}),D("\u5DF2\u4FDD\u5B58","ok"),this.edit=null,await this.load()}catch(e){D(Z(e),"err")}},async delItem(e){let t=(this.fsPath?this.fsPath+"/":"")+e.name;if(confirm("\u5220\u9664\u300C"+t+"\u300D\uFF1F"))try{await Y("qqbot.tools.fs",{action:"delete",path:t}),await this.load()}catch(i){D(Z(i),"err")}},openTest(e){let t={web_search:{query:"\u4ECA\u5929\u7684\u65B0\u95FB"},calc:{expression:"sqrt(2)*10 + 3**2"},convert:{value:100,from:"km",to:"mi"},random:{kind:"dice",sides:6,count:2},codec:{action:"sha256",text:"hello"},date_calc:{action:"diff",date1:"2026-01-01",date2:"2026-11-08"}};this.test={id:e.id,args:JSON.stringify(t[e.id]||{},null,2)},this.testOut=""},async runTest(){if(this.test){this.busy="test";try{let e=JSON.parse(this.test.args||"{}"),t=await Y("qqbot.tools.test",{id:this.test.id,args:e});this.testOut=JSON.stringify(t&&t.result,null,2)}catch(e){this.testOut="\u5931\u8D25\uFF1A"+Z(e)}finally{this.busy=""}}}},template:`
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-pnl">
      <div class="rcq-flex">
        <b>\u7CFB\u7EDF\u5185\u7F6E\u5DE5\u5177</b>
        <span class="rcq-hint">AI \u6309\u9700\u8C03\u7528\uFF1B\u53EA\u505A\u7CFB\u7EDF\u5185\u7F6E\uFF0C\u4E0D\u5F00\u653E\u81EA\u5B9A\u4E49</span>
        <span style="margin-left:auto"></span>
        <button class="btn btn-sm btn-primary" :disabled="!!busy" @click="saveCfg">\u4FDD\u5B58</button>
      </div>
      <div v-for="t in tools" :key="t.id" class="rcq-flex"
        style="padding:9px 0;border-bottom:1px solid var(--bd)">
        <label class="switch"><input type="checkbox" v-model="enabled[t.id]" /><span class="slider"></span></label>
        <b style="margin-left:8px">{{ t.name }}</b>
        <span class="rcq-hint" style="margin-left:6px">{{ t.desc }}</span>
        <span style="margin-left:auto"></span>
        <span class="rcq-badge" :class="t.category === 'workspace' ? 'warn' : 'ok'">
          {{ t.category === 'workspace' ? '\u5DE5\u4F5C\u533A' : '\u8F85\u52A9' }}</span>
        <button class="btn btn-sm" style="margin-left:8px" @click="openTest(t)">\u6D4B\u8BD5</button>
      </div>
    </div>

    <div class="rcq-pnl">
      <div class="rcq-flex">
        <b>\u5DE5\u4F5C\u533A</b>
        <span class="rcq-hint">{{ ws.files }} \u4E2A\u6587\u4EF6 \xB7 {{ fmtSize(ws.bytes) }} / {{ ws.max_mb }} MB</span>
        <span style="margin-left:auto"></span>
        <label class="rcq-hint">\u914D\u989D(MB)</label>
        <input class="input" type="number" min="1" max="1024" style="width:90px" v-model.number="ws.max_mb" />
        <button class="btn btn-sm" @click="saveCfg">\u5E94\u7528</button>
      </div>
      <div class="rcq-note" style="word-break:break-all">
        {{ ws.root }} \u2014\u2014 AI \u53EA\u80FD\u5728\u8FD9\u4E2A\u76EE\u5F55\u5185\u8BFB\u5199\uFF0C\u521D\u59CB\u4E3A\u7A7A\u3002
      </div>
      <div class="rcq-flex" style="margin-top:8px">
        <button class="btn btn-sm" @click="fsUp" :disabled="!fsPath">\u2191 \u4E0A\u4E00\u7EA7</button>
        <span class="rcq-hint" style="margin-left:6px">/{{ fsPath }}</span>
        <span style="margin-left:auto"></span>
        <button class="btn btn-sm" @click="newFile">\u65B0\u5EFA\u6587\u4EF6</button>
        <button class="btn btn-sm" @click="newDir">\u65B0\u5EFA\u76EE\u5F55</button>
        <button class="btn btn-sm" @click="fsList(fsPath)">\u5237\u65B0</button>
      </div>
      <div v-for="it in fsItems" :key="it.name" class="rcq-flex"
        style="padding:7px 0;border-bottom:1px solid var(--bd)">
        <span style="cursor:pointer" @click="fsGo(it)">
          {{ it.is_dir ? '\u{1F4C1}' : '\u{1F4C4}' }} {{ it.name }}</span>
        <span class="rcq-hint" style="margin-left:auto">{{ it.is_dir ? '' : fmtSize(it.size) }}</span>
        <button class="btn btn-sm" style="margin-left:8px" @click="delItem(it)">\u5220\u9664</button>
      </div>
      <div v-if="!fsItems.length" class="rcq-hint" style="margin-top:8px">\u7A7A\u76EE\u5F55</div>
    </div>

    <div v-if="edit" class="rcq-mask" @click.self="edit = null">
      <div class="rcq-modal">
        <div class="rcq-flex"><b class="mono" style="word-break:break-all">{{ edit.path }}</b>
          <span style="margin-left:auto"></span>
          <button class="btn btn-sm" @click="edit = null">\u5173\u95ED</button></div>
        <textarea class="input" rows="16" v-model="edit.content" style="margin-top:10px"></textarea>
        <div class="rcq-acts" style="margin-top:10px">
          <button class="btn btn-primary" @click="saveFile">\u4FDD\u5B58</button>
          <button class="btn" @click="edit = null">\u53D6\u6D88</button>
        </div>
      </div>
    </div>

    <div v-if="test" class="rcq-mask" @click.self="test = null">
      <div class="rcq-modal">
        <div class="rcq-flex"><b>\u6D4B\u8BD5 {{ test.id }}</b>
          <span style="margin-left:auto"></span>
          <button class="btn btn-sm" @click="test = null">\u5173\u95ED</button></div>
        <div class="rcq-fi" style="margin-top:10px"><span>\u53C2\u6570\uFF08JSON\uFF09</span>
          <textarea class="input" rows="4" v-model="test.args"></textarea></div>
        <div class="rcq-acts" style="margin-top:10px">
          <button class="btn btn-primary" :disabled="busy === 'test'" @click="runTest">\u8FD0\u884C</button>
        </div>
        <pre v-if="testOut" style="margin-top:10px;white-space:pre-wrap;max-height:260px;overflow:auto;background:var(--sf2);padding:10px;border-radius:8px;font-size:12px">{{ testOut }}</pre>
      </div>
    </div>
  </div>`},Hm={data(){return{tab:"menu",loading:!0,busy:"",err:"",cfg:null,images:{},previewText:"",edit:null,selPool:"",selImg:""}},computed:{items(){return this.cfg&&this.cfg.items||[]},pools(){return this.cfg&&this.cfg.text_pools||[]},ipools(){return this.cfg&&this.cfg.image_pools||[]},curPool(){return this.pools.find(e=>e.id===this.selPool)||this.pools[0]||null},curImg(){return this.ipools.find(e=>e.id===this.selImg)||this.ipools[0]||null}},async mounted(){await this.load()},methods:{async load(){this.loading=!0;try{let e=await Y("qqbot.panel.get",{});this.cfg=e&&e.panel||{items:[],text_pools:[],image_pools:[]},this.images=e&&e.images||{},this.selPool||(this.selPool=(this.cfg.text_pools[0]||{}).id||""),this.selImg||(this.selImg=(this.cfg.image_pools[0]||{}).id||"")}catch(e){this.err=Z(e)}finally{this.loading=!1}},async save(){this.busy="save";try{await Y("qqbot.panel.save",{panel:this.cfg}),D("\u9762\u677F\u5DF2\u4FDD\u5B58","ok")}catch(e){D(Z(e),"err")}finally{this.busy=""}},async previewMenu(){try{let e=await Y("qqbot.panel.preview",{mode:"menu"});this.previewText=e&&e.text||""}catch(e){D(Z(e),"err")}},async previewItem(e){try{let t=await Y("qqbot.panel.preview",{mode:"feature",id:e.id});this.previewText=(t&&t.text||"")+(t&&t.image?`
[\u56FE\u7247] `+t.image:"")}catch(t){D(Z(t),"err")}},addItem(){this.edit={id:"item_"+Date.now().toString(36),name:"",aliases:[],desc:"",type:"content",text_pool:(this.pools[0]||{}).id||"",image_pool:(this.ipools[0]||{}).id||"",cooldown:5,show_in_menu:!0,enabled:!0,text:""}},editItem(e){this.edit=JSON.parse(JSON.stringify(e))},saveEdit(){let e=this.edit;if(!e||!String(e.name||"").trim()){D("\u540D\u79F0\u4E0D\u80FD\u4E3A\u7A7A","err");return}let t=this.items.findIndex(i=>i.id===e.id);t>=0?this.cfg.items.splice(t,1,e):this.cfg.items.push(e),this.edit=null,this.save()},delItem(e){confirm("\u5220\u9664\u529F\u80FD\u9879\u300C"+(this.items[e].name||"")+"\u300D\uFF1F")&&(this.cfg.items.splice(e,1),this.save())},moveItem(e,t){let i=e+t;if(i<0||i>=this.items.length)return;let s=this.cfg.items[e];this.cfg.items[e]=this.cfg.items[i],this.cfg.items[i]=s,this.save()},aliasesStr(e){return(e.aliases||[]).join(", ")},setAliases(e,t){e.aliases=String(t||"").split(/[,，\s]+/).filter(Boolean)},levelsStr(e){return(e.levels||[]).join(", ")},setLevels(e,t){e.levels=String(t||"").split(/[,，\s]+/).filter(Boolean)},poolText(e){return(e.items||[]).filter(t=>!t.source||t.source==="manual").map(t=>typeof t=="string"?t:t.text||"").join(`
`)},setPoolText(e,t){let i=(e.items||[]).filter(n=>n.source==="ai"),s=String(t||"").split(`
`).map(n=>n.trim()).filter(Boolean);e.items=s.map((n,r)=>({id:"m"+r,text:n,source:"manual"})).concat(i)},aiOf(e){return e.ai_daily||(e.ai_daily={enabled:!1,count:10,time:"00:10",keep_max:300}),e.ai_daily},addTextPool(){let e="pool_"+Date.now().toString(36);this.cfg.text_pools=this.cfg.text_pools||[],this.cfg.text_pools.push({id:e,name:"\u65B0\u6587\u672C\u7EC4",enabled:!0,items:[],ai_daily:{enabled:!1,count:10,time:"00:10",keep_max:300,prompt:""}}),this.selPool=e,this.save()},delTextPool(){let e=this.curPool;!e||!confirm("\u5220\u9664\u6587\u672C\u7EC4\u300C"+e.name+"\u300D\uFF1F")||(this.cfg.text_pools=this.pools.filter(t=>t.id!==e.id),this.selPool=(this.cfg.text_pools[0]||{}).id||"",this.save())},addImgPool(){let e="img_"+Date.now().toString(36);this.cfg.image_pools=this.cfg.image_pools||[],this.cfg.image_pools.push({id:e,name:"\u65B0\u56FE\u7247\u7EC4",enabled:!0,source:"api",items:[],api:{url:"",timeout:10,max_bytes:8388608,max_redirects:3}}),this.selImg=e,this.save()},delImgPool(){let e=this.curImg;!e||!confirm("\u5220\u9664\u56FE\u7247\u7EC4\u300C"+e.name+"\u300D\uFF1F")||(this.cfg.image_pools=this.ipools.filter(t=>t.id!==e.id),this.selImg=(this.cfg.image_pools[0]||{}).id||"",this.save())},async generate(e){this.busy="gen";try{let t=await Y("qqbot.panel.generate",{pool_id:e.id,count:Number(this.aiOf(e).count)||10},{timeoutMs:18e4});D("\u5DF2\u751F\u6210 "+(t&&t.added||0)+" \u6761","ok"),await this.load()}catch(t){D(Z(t),"err")}finally{this.busy=""}},async uploadImage(e){let t=e.target.files&&e.target.files[0];if(e.target.value="",!t||!this.curImg)return;let i=await new Promise(s=>{let n=new FileReader;n.onload=()=>s(String(n.result||"")),n.readAsDataURL(t)});this.busy="upload";try{let s=await Y("qqbot.panel.image_upload",{pool_id:this.curImg.id,name:t.name,data:i});s&&s.name&&(this.curImg.items=this.curImg.items||[],this.curImg.items.push(s.name),await this.save()),await this.load(),D("\u5DF2\u4E0A\u4F20","ok")}catch(s){D(Z(s),"err")}finally{this.busy=""}},imgUrl(e){let i=(this.images[(this.curImg||{}).id]||[]).find(s=>s.name===e);return i?"/api/fm/preview?path="+encodeURIComponent(i.abs):""},fmtSize(e){return e=Number(e)||0,e>=1048576?(e/1048576).toFixed(1)+"MB":Math.round(e/1024)+"KB"}},template:`
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-pnl">
      <div class="rcq-flex">
        <button class="btn btn-sm" :class="tab === 'menu' ? 'btn-primary' : ''" @click="tab = 'menu'">\u83DC\u5355</button>
        <button class="btn btn-sm" :class="tab === 'text' ? 'btn-primary' : ''" @click="tab = 'text'">\u6587\u672C\u5E93</button>
        <button class="btn btn-sm" :class="tab === 'image' ? 'btn-primary' : ''" @click="tab = 'image'">\u56FE\u7247\u5E93</button>
        <span style="margin-left:auto"></span>
        <button class="btn btn-sm btn-primary" :disabled="!!busy" @click="save">
          {{ busy === 'save' ? '\u4FDD\u5B58\u4E2D\u2026' : '\u4FDD\u5B58' }}</button>
      </div>
    </div>

    <template v-if="tab === 'menu' && cfg">
      <div class="rcq-pnl">
        <div class="rcq-grid">
          <label class="rcq-fi"><span>\u6807\u9898</span>
            <input class="input" v-model="cfg.title" /></label>
          <label class="rcq-fi"><span>\u89E6\u53D1\u8BCD\uFF08\u9017\u53F7\u5206\u9694\uFF09</span>
            <input class="input" :value="(cfg.triggers || []).join(', ')"
              @input="cfg.triggers = $event.target.value.split(/[,\uFF0C\\s]+/).filter(Boolean)" /></label>
          <label class="rcq-fi"><span>\u5E95\u90E8\u63D0\u793A</span>
            <input class="input" v-model="cfg.hint" /></label>
          <div class="rcq-acts">
            <label class="rcq-fi" style="margin:0"><span>\u6BCF\u9875\u6761\u6570</span>
              <input class="input" type="number" min="1" max="20" v-model.number="cfg.page_size" style="width:90px" /></label>
            <button class="btn btn-sm" @click="previewMenu">\u9884\u89C8\u83DC\u5355</button>
            <button class="btn btn-sm" @click="addItem">+ \u529F\u80FD</button>
          </div>
        </div>
        <pre v-if="previewText" style="margin-top:10px;white-space:pre-wrap;background:var(--sf2);padding:10px;border-radius:8px;font-size:12.5px">{{ previewText }}</pre>
      </div>

      <div class="rcq-pnl">
        <div v-for="(it, i) in items" :key="it.id" class="rcq-flex"
          style="padding:9px 0;border-bottom:1px solid var(--bd)">
          <b style="min-width:110px">{{ it.name || '(\u672A\u547D\u540D)' }}</b>
          <span class="rcq-hint">{{ it.type }}<template v-if="it.aliases && it.aliases.length"> \xB7 {{ aliasesStr(it) }}</template></span>
          <span style="margin-left:auto"></span>
          <button class="btn btn-sm" @click="moveItem(i, -1)" :disabled="i === 0">\u2191</button>
          <button class="btn btn-sm" @click="moveItem(i, 1)" :disabled="i === items.length - 1">\u2193</button>
          <button class="btn btn-sm" @click="previewItem(it)">\u9884\u89C8</button>
          <button class="btn btn-sm" @click="editItem(it)">\u7F16\u8F91</button>
          <button class="btn btn-sm" @click="delItem(i)">\u5220\u9664</button>
        </div>
        <div v-if="!items.length" class="rcq-empty2">\u8FD8\u6CA1\u6709\u529F\u80FD\u9879</div>
      </div>
    </template>

    <template v-if="tab === 'text' && cfg">
      <div class="rcq-pnl">
        <div class="rcq-flex">
          <select class="input" style="width:220px" v-model="selPool">
            <option v-for="p in pools" :key="p.id" :value="p.id">{{ p.name }}\uFF08{{ (p.items || []).length }} \u6761\uFF09</option>
          </select>
          <button class="btn btn-sm" @click="addTextPool">+ \u65B0\u5EFA</button>
          <button class="btn btn-sm" @click="delTextPool">\u5220\u9664</button>
          <span style="margin-left:auto"></span>
          <button class="btn btn-sm" :disabled="busy === 'gen'" @click="generate(curPool)">
            {{ busy === 'gen' ? '\u751F\u6210\u4E2D\u2026' : '\u7ACB\u5373\u751F\u6210' }}</button>
        </div>
      </div>

      <div v-if="curPool" class="rcq-pnl">
        <label class="rcq-fi"><span>\u6587\u672C\u7EC4\u540D\u79F0</span>
          <input class="input" v-model="curPool.name" /></label>
        <div class="rcq-fi" style="margin-top:10px"><span>\u6587\u6848\uFF08\u6BCF\u884C\u4E00\u6761\uFF1BAI \u751F\u6210\u7684\u6761\u76EE\u5728\u4E0B\u65B9\u5355\u72EC\u5217\u51FA\uFF09</span>
          <textarea class="input" rows="10" :value="poolText(curPool)"
            @input="setPoolText(curPool, $event.target.value)"></textarea></div>

        <div class="rcq-flex" style="margin-top:12px">
          <b>AI \u6BCF\u65E5\u751F\u6210</b>
          <label class="rcq-hint"><input type="checkbox" v-model="aiOf(curPool).enabled" /> \u542F\u7528</label>
          <span class="rcq-hint">\u6BCF\u5929</span>
          <input class="input" style="width:90px" v-model="aiOf(curPool).time" placeholder="00:10" />
          <span class="rcq-hint">\u751F\u6210</span>
          <input class="input" type="number" min="1" max="50" style="width:80px" v-model.number="aiOf(curPool).count" />
          <span class="rcq-hint">\u6761 \xB7 \u4FDD\u7559\u4E0A\u9650</span>
          <input class="input" type="number" min="0" style="width:90px" v-model.number="aiOf(curPool).keep_max" />
        </div>
        <div class="rcq-fi" style="margin-top:8px"><span>\u751F\u6210\u63D0\u793A\u8BCD\uFF08\u7559\u7A7A\u7528\u9ED8\u8BA4\uFF09</span>
          <textarea class="input" rows="3" v-model="aiOf(curPool).prompt"></textarea></div>
        <div class="rcq-hint" style="margin-top:6px">
          \u4E0A\u6B21\uFF1A{{ aiOf(curPool).last_run_date || '\u2014' }} \xB7 {{ aiOf(curPool).last_run_count || 0 }} \u6761
        </div>

        <div v-if="(curPool.items || []).some(x => x.source === 'ai')" style="margin-top:12px">
          <b>AI \u6761\u76EE</b>
          <div v-for="(x, i) in (curPool.items || [])" :key="i">
            <div v-if="x.source === 'ai'" class="rcq-flex" style="padding:6px 0;border-bottom:1px solid var(--bd)">
              <span style="font-size:12.5px">{{ x.text }}</span>
              <span class="rcq-hint" style="margin-left:8px;flex:none">{{ x.gen_date }}</span>
              <span style="margin-left:auto"></span>
              <button class="btn btn-sm" @click="curPool.items.splice(i, 1); save()">\u5220\u9664</button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-if="tab === 'image' && cfg">
      <div class="rcq-pnl">
        <div class="rcq-flex">
          <select class="input" style="width:220px" v-model="selImg">
            <option v-for="p in ipools" :key="p.id" :value="p.id">{{ p.name }}\uFF08{{ p.source }}\uFF09</option>
          </select>
          <button class="btn btn-sm" @click="addImgPool">+ \u65B0\u5EFA</button>
          <button class="btn btn-sm" @click="delImgPool">\u5220\u9664</button>
          <span style="margin-left:auto"></span>
          <label class="btn btn-sm" style="margin:0">\u4E0A\u4F20\u56FE\u7247
            <input type="file" accept="image/*" hidden @change="uploadImage" /></label>
        </div>
      </div>

      <div v-if="curImg" class="rcq-pnl">
        <div class="rcq-grid">
          <label class="rcq-fi"><span>\u56FE\u7247\u7EC4\u540D\u79F0</span>
            <input class="input" v-model="curImg.name" /></label>
          <label class="rcq-fi"><span>\u6765\u6E90</span>
            <select class="input" v-model="curImg.source">
              <option value="api">\u5916\u90E8\u56FE\u7247 API</option>
              <option value="local">\u672C\u5730\u56FE\u7247</option>
            </select></label>
        </div>
        <div v-if="curImg.source === 'api'" class="rcq-grid" style="margin-top:10px">
          <label class="rcq-fi" style="grid-column:1/-1"><span>API \u5730\u5740\uFF08302 \u6700\u591A\u8DDF 3 \u8DF3\uFF09</span>
            <input class="input" v-model="curImg.api.url" placeholder="https://www.loliapi.com/acg/pe/" /></label>
          <label class="rcq-fi"><span>\u8D85\u65F6\uFF08\u79D2\uFF09</span>
            <input class="input" type="number" v-model.number="curImg.api.timeout" /></label>
          <label class="rcq-fi"><span>\u6700\u5927\u4F53\u79EF\uFF08MB\uFF09</span>
            <input class="input" type="number" :value="Math.round((curImg.api.max_bytes || 8388608) / 1048576)"
              @input="curImg.api.max_bytes = (Number($event.target.value) || 8) * 1048576" /></label>
        </div>
        <div v-else style="margin-top:10px">
          <div style="display:flex;flex-wrap:wrap;gap:8px">
            <div v-for="n in (curImg.items || [])" :key="n" style="width:110px">
              <img :src="imgUrl(n)" style="width:100%;height:80px;object-fit:cover;border-radius:8px"
                @error="$event.target.style.opacity = 0.25" />
              <div class="rcq-flex" style="margin-top:4px">
                <span class="rcq-hint" style="overflow:hidden;text-overflow:ellipsis">{{ n }}</span>
                <button class="btn btn-sm" style="margin-left:auto" @click="curImg.items = curImg.items.filter(v => v !== n); save()">\xD7</button>
              </div>
            </div>
          </div>
          <div v-if="!(curImg.items || []).length" class="rcq-hint" style="margin-top:6px">\u8FD8\u6CA1\u6709\u672C\u5730\u56FE\u7247\uFF0C\u70B9\u53F3\u4E0A\u89D2\u4E0A\u4F20</div>
        </div>
      </div>
    </template>

    <div v-if="edit" class="rcq-mask" @click.self="edit = null">
      <div class="rcq-modal">
        <div class="rcq-flex"><b>\u529F\u80FD\u9879</b><span style="margin-left:auto"></span>
          <button class="btn btn-sm" @click="edit = null">\u5173\u95ED</button></div>
        <div class="rcq-grid" style="margin-top:10px">
          <label class="rcq-fi"><span>\u540D\u79F0</span><input class="input" v-model="edit.name" /></label>
          <label class="rcq-fi"><span>\u522B\u540D\uFF08\u9017\u53F7\u5206\u9694\uFF09</span>
            <input class="input" :value="aliasesStr(edit)" @input="setAliases(edit, $event.target.value)" /></label>
          <label class="rcq-fi"><span>\u8BF4\u660E</span><input class="input" v-model="edit.desc" /></label>
          <label class="rcq-fi"><span>\u7C7B\u578B</span>
            <select class="input" v-model="edit.type">
              <option value="content">\u6587\u672C\u5E93 + \u56FE\u7247\u5E93</option>
              <option value="text">\u56FA\u5B9A\u6587\u672C</option>
            </select></label>
          <label class="rcq-fi"><span>\u6587\u672C\u7EC4</span>
            <select class="input" v-model="edit.text_pool">
              <option value="">\u4E0D\u4F7F\u7528</option>
              <option v-for="p in pools" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select></label>
          <label class="rcq-fi"><span>\u56FE\u7247\u7EC4</span>
            <select class="input" v-model="edit.image_pool">
              <option value="">\u4E0D\u4F7F\u7528</option>
              <option v-for="p in ipools" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select></label>
          <label class="rcq-fi"><span>\u51B7\u5374\uFF08\u79D2\uFF09</span>
            <input class="input" type="number" v-model.number="edit.cooldown" /></label>
          <template v-if="edit.type === 'content'">
            <label class="rcq-fi"><span>\u8FD0\u52BF\u7B49\u7EA7\uFF08\u9017\u53F7\u5206\u9694\uFF0C\u7559\u7A7A\u4E0D\u663E\u793A\uFF09</span>
              <input class="input" :value="levelsStr(edit)" @input="setLevels(edit, $event.target.value)" /></label>
            <label class="rcq-fi"><span>\u7B49\u7EA7\u524D\u7F00</span>
              <input class="input" v-model="edit.level_prefix" placeholder="\u8FD0\u52BF" /></label>
          </template>
          <label class="rcq-fi"><span>\u83DC\u5355\u663E\u793A</span>
            <label class="rcq-hint"><input type="checkbox" v-model="edit.show_in_menu" /> \u663E\u793A</label></label>
        </div>
        <div v-if="edit.type === 'text'" class="rcq-fi" style="margin-top:10px">
          <span>\u56FA\u5B9A\u6587\u672C</span><textarea class="input" rows="4" v-model="edit.text"></textarea></div>
        <div class="rcq-acts" style="margin-top:12px">
          <button class="btn btn-primary" @click="saveEdit">\u4FDD\u5B58</button>
          <button class="btn" @click="edit = null">\u53D6\u6D88</button>
        </div>
      </div>
    </div>
  </div>`},hp=[{id:"im",label:"\u6D88\u606F",comp:op},{id:"overview",label:"\u6982\u89C8",comp:Pm},{id:"account",label:"QQ \u8D26\u6237",comp:jm},{id:"query",label:"\u67E5\u8BE2",comp:Fm},{id:"media",label:"\u5A92\u4F53\u5E93",comp:Lm},{id:"cards",label:"\u89D2\u8272\u5361\u7247",comp:zm},{id:"sessions",label:"\u4F1A\u8BDD\u7BA1\u7406",comp:Bm},{id:"providers",label:"\u6A21\u578B\u63D0\u4F9B\u5546",comp:Dm},{id:"tools",label:"\u5DE5\u5177\u94FE",comp:Vm},{id:"panel",label:"\u9762\u677F",comp:Hm},{id:"logs",label:"\u8FD0\u884C\u65E5\u5FD7",comp:$m},{id:"settings",label:"\u8BBE\u7F6E",comp:Um}],Km={data(){let e="overview";try{let t=localStorage.getItem(up);t&&hp.some(i=>i.id===t)&&(e=t)}catch{}return{S:yt,tab:e,TABS:hp,conn:null,key:0}},computed:{cur(){return(this.TABS.find(e=>e.id===this.tab)||this.TABS[0]).comp},slOn(){return!!(this.conn&&this.conn.snowluma&&this.conn.snowluma.ok)},rbOn(){return!!(this.conn&&this.conn.rcbot&&this.conn.rcbot.ok)}},async mounted(){await this.check()},methods:{async check(){try{this.conn=await Ue("qqbot.conn.get")}catch{}},go(e){this.tab=e;try{localStorage.setItem(up,e)}catch{}this.check()},onImClose(){this.go("overview")},refresh(){this.key++,this.check()}},template:`
  <div class="rcq" :class="{ 'rcq-im-mode': tab === 'im' }">
    <div class="rcq-bar">
      <div class="rcq-tab" v-for="t in TABS" :key="t.id" :class="{ on: tab === t.id }"
        @click="go(t.id)">{{ t.label }}</div>
      <div class="rcq-bar-r">
        <span class="rcq-lamp"><b :class="slOn ? 'on' : 'off'"></b>SnowLuma</span>
        <span class="rcq-lamp"><b :class="rbOn ? 'on' : 'off'"></b>Bot</span>
        <button class="btn btn-sm" @click="refresh">\u5237\u65B0</button>
      </div>
    </div>

    <component :is="cur" :key="tab + '-' + key" @close="onImClose" />

    <div class="rcq-toast" v-if="S.toast" :class="S.toastKind">{{ S.toast }}</div>
  </div>`};function Qm(e,t){Rm(),dp(),Ir=t,Qd(t);let i=Bs(Km),s=()=>{try{i.unmount()}catch{}};return i.mount(e),s}function Wm(e){e.__rcPluginV4__=e.__rcPluginV4__||{},e.__rcPluginV4__[Im]={pages:[{path:"",title:"QQ Bot"}],mount:Qm}}typeof window<"u"&&Wm(window);})();
