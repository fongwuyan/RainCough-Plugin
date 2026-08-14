import java.io.UnsupportedEncodingException;

/**
 * @author lazy
 * @since 2025-12-30
 * 文件类型枚举
 */
public enum FileType {
    // 图片格式
    JPG("jpg", new int[][]{
            {0xFF, 0xD8, 0xFF, 0xE0}, // JFIF
            {0xFF, 0xD8, 0xFF, 0xE1}, // Exif
            {0xFF, 0xD8, 0xFF, 0xE8}  // SPIFF
    }),
    PNG("png", new int[][]{
            {0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A}
    }),
    GIF("gif", new int[][]{
            {0x47, 0x49, 0x46, 0x38, 0x37, 0x61}, // GIF87a
            {0x47, 0x49, 0x46, 0x38, 0x39, 0x61}  // GIF89a
    }),
    BMP("bmp", new int[][]{
            {0x42, 0x4D}
    }),
    TIFF("tiff", new int[][]{
            {0x49, 0x49, 0x2A, 0x00}, // 小端
            {0x4D, 0x4D, 0x00, 0x2A}  // 大端
    }),
    WEBP("webp", new int[][]{
            {0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00, 0x57, 0x45, 0x42, 0x50} // RIFF....WEBP
    }),

    // 文档格式
    PDF("pdf", new int[][]{
            {0x25, 0x50, 0x44, 0x46, 0x2D} // %PDF-
    }),
    DOC("doc", new int[][]{
            {0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1} // 旧版Office
    }),
    DOCX("docx", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5B, 0x43, 0x6F, 0x6E, 0x74, 0x65, 0x6E, 0x74, 0x5F, 0x54, 0x79, 0x70, 0x65, 0x73, 0x5D, 0x2E, 0x78, 0x6D, 0x6C} // 包含[Content_Types].xml
    }),

    XLSX("xlsx", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78, 0x6C, 0x2F, 0x77, 0x6F, 0x72, 0x6B, 0x62, 0x6F, 0x6F, 0x6B, 0x2E, 0x78, 0x6D, 0x6C} // 包含xl/workbook.xml
    }),

    PPTX("pptx", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x70, 0x70, 0x74, 0x2F, 0x70, 0x72, 0x65, 0x73, 0x65, 0x6E, 0x74, 0x61, 0x74, 0x69, 0x6F, 0x6E, 0x2E, 0x78, 0x6D, 0x6C} // 包含ppt/presentation.xml
    }),
    // 添加更多Office相关格式
    XLS("xls", new int[][]{
            {0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3E, 0x00, 0x03, 0x00, 0xFE, 0xFF, 0x09, 0x00, 0x06, 0x00} // 复合文档 + Excel特定
    }),

    PPT("ppt", new int[][]{
            {0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3E, 0x00, 0x03, 0x00, 0xFE, 0xFF, 0x0A, 0x00, 0x06, 0x00} // 复合文档 + PowerPoint特定
    }),
    RTF("rtf", new int[][]{
            {0x7B, 0x5C, 0x72, 0x74, 0x66} // {\rtf
    }),
    //APK
    APK("apk", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x08, 0x00, 0x08, 0x00} // ZIP + 特定标志
    }),
    DEX("dex", new int[][]{
            {0x64, 0x65, 0x78, 0x0A, 0x30, 0x33, 0x35, 0x00} // dex\n035\0
    }),

    // Android相关 - 检查ZIP包内的特定目录结构
    AAB("aab", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00} // 特定AAB结构
    }),

    // iOS相关 - IPA有特定的目录结构
    IPA("ipa", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x50, 0x61, 0x79, 0x6C, 0x6F, 0x61, 0x64, 0x73} // 包含Payloads目录
    }),

    // Windows安装包
    MSI("msi", new int[][]{
            {0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3E, 0x00} // 复合文档特定结构
    }),

    // Linux软件包
    DEB("deb", new int[][]{
            {0x21, 0x3C, 0x61, 0x72, 0x63, 0x68, 0x3E, 0x0A, 0x64, 0x65, 0x62, 0x69, 0x61, 0x6E, 0x2D, 0x62, 0x69, 0x6E, 0x61, 0x72, 0x79} // !<arch>\ndebian-binary
    }),
    RPM("rpm", new int[][]{
            {0xED, 0xAB, 0xEE, 0xDB, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00} // RPM签名头
    }),

    // macOS相关
    DMG("dmg", new int[][]{
            {0x78, 0x01, 0x73, 0x0D, 0x62, 0x62, 0x60, 0x72, 0x65, 0x73, 0x6F, 0x75, 0x72, 0x63, 0x65, 0x2D, 0x66, 0x6F, 0x72, 0x6B} // UDIF资源分支
    }),
    PKG("pkg", new int[][]{
            {0x78, 0x61, 0x72, 0x21, 0x00, 0x1C, 0x00, 0x01, 0x00, 0x00, 0x00} // xar!头部
    }),

    // Windows应用包
    APPX("appx", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5B, 0x44, 0x53, 0x5D} // 包含[DS]签名
    }),

    // 游戏相关
    APK_EXPANSION("obb", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x6D, 0x61, 0x69, 0x6E} // 通常包含main或patch
    }),
    UNITY_ASSET("unity3d", new int[][]{
            {0x55, 0x6E, 0x69, 0x74, 0x79, 0x46, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00} // UnityFS头部
    }),
    UNITY_WEB("unityweb", new int[][]{
            {0x55, 0x6E, 0x69, 0x74, 0x79, 0x57, 0x65, 0x62, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00} // UnityWeb头部
    }),

    // Java相关
    JAR("jar", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x08, 0x00, 0x08, 0x00, 0x4D, 0x45, 0x54, 0x41, 0x2D, 0x49, 0x4E, 0x46} // 包含META-INF
    }),
    WAR("war", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x08, 0x00, 0x08, 0x00, 0x57, 0x45, 0x42, 0x2D, 0x49, 0x4E, 0x46} // 包含WEB-INF
    }),

    // 其他常见格式
    EPUB("epub", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x6D, 0x69, 0x6D, 0x65, 0x74, 0x79, 0x70, 0x65} // 包含mimetype
    }),
    ODT("odt", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x6D, 0x69, 0x6D, 0x65, 0x74, 0x79, 0x70, 0x65, 0x61, 0x70, 0x70, 0x6C, 0x69, 0x63, 0x61, 0x74, 0x69, 0x6F, 0x6E, 0x2F, 0x76, 0x6E, 0x64, 0x2E, 0x6F, 0x61, 0x73, 0x69, 0x73, 0x2E, 0x6F, 0x70, 0x65, 0x6E, 0x64, 0x6F, 0x63, 0x75, 0x6D, 0x65, 0x6E, 0x74, 0x2E, 0x74, 0x65, 0x78, 0x74} // OpenDocument文本
    }),
    ODS("ods", new int[][]{
            {0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x6D, 0x69, 0x6D, 0x65, 0x74, 0x79, 0x70, 0x65, 0x61, 0x70, 0x70, 0x6C, 0x69, 0x63, 0x61, 0x74, 0x69, 0x6F, 0x6E, 0x2F, 0x76, 0x6E, 0x64, 0x2E, 0x6F, 0x61, 0x73, 0x69, 0x73, 0x2E, 0x6F, 0x70, 0x65, 0x6E, 0x64, 0x6F, 0x63, 0x75, 0x6D, 0x65, 0x6E, 0x74, 0x2E, 0x73, 0x70, 0x72, 0x65, 0x61, 0x64, 0x73, 0x68, 0x65, 0x65, 0x74} // OpenDocument表格
    }),
    // 压缩文件
    RAR("rar", new int[][]{
            {0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x00},       // RAR 4.x
            {0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x01, 0x00}  // RAR 5.x
    }),
    SEVEN_Z("7z", new int[][]{
            {0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C}
    }),
    GZIP("gz", new int[][]{
            {0x1F, 0x8B, 0x08} // 压缩方法8
    }),
    TAR("tar", new int[][]{
            {0x75, 0x73, 0x74, 0x61, 0x72} // ustar
    }),

    // 音频格式
    MP3("mp3", new int[][]{
            {0x49, 0x44, 0x33},               // ID3v2标签
            {0xFF, 0xFB},                     // MPEG Layer 3, 128kbps
            {0xFF, 0xF3},                     // MPEG Layer 3, 可变比特率
            {0xFF, 0xF2}                      // MPEG Layer 3, 立体声
    }),
    WAV("wav", new int[][]{
            {0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00, 0x57, 0x41, 0x56, 0x45} // RIFF....WAVE
    }),
    FLAC("flac", new int[][]{
            {0x66, 0x4C, 0x61, 0x43} // fLaC
    }),
    OGG("ogg", new int[][]{
            {0x4F, 0x67, 0x67, 0x53} // OggS
    }),
    AAC("aac", new int[][]{
            {0xFF, 0xF1}, // ADTS AAC
            {0xFF, 0xF9}  // ADTS AAC
    }),

    // 视频格式
    MP4("mp4", new int[][]{
            {0,0,0,0x20,0x66,0x74,0x79,0x70},
            {0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70, 0x69, 0x73, 0x6F, 0x6D}, // isom
            {0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70, 0x6D, 0x70, 0x34, 0x32}, // mp42
            {0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70, 0x61, 0x76, 0x63, 0x31}  // avc1
    }),
    AVI("avi", new int[][]{
            {0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00, 0x41, 0x56, 0x49, 0x20} // RIFF....AVI
    }),
    MKV("mkv", new int[][]{
            {0x1A, 0x45, 0xDF, 0xA3}
    }),
    FLV("flv", new int[][]{
            {0x46, 0x4C, 0x56, 0x01} // FLV
    }),
    MOV("mov", new int[][]{
            {0x00, 0x00, 0x00, 0x14, 0x66, 0x74, 0x79, 0x70, 0x71, 0x74, 0x20, 0x20} // ftypqt
    }),

    // 可执行文件
    EXE("exe", new int[][]{
            {0x4D, 0x5A} // MZ
    }),
    ELF("elf", new int[][]{
            {0x7F, 0x45, 0x4C, 0x46, 0x01}, // 32位
            {0x7F, 0x45, 0x4C, 0x46, 0x02}  // 64位
    }),
    MACH_O("macho", new int[][]{
            {0xFE, 0xED, 0xFA, 0xCE}, // 32位大端
            {0xCE, 0xFA, 0xED, 0xFE}, // 32位小端
            {0xFE, 0xED, 0xFA, 0xCF}, // 64位大端
            {0xCF, 0xFA, 0xED, 0xFE}  // 64位小端
    }),

    // 其他
    TXT("txt", new int[][]{
            {} // 无固定文件头
    }),
    XML("xml", new int[][]{
            {0x3C, 0x3F, 0x78, 0x6D, 0x6C, 0x20} // <?xml
    }),
    HTML("html", new int[][]{
            {0x3C, 0x21, 0x44, 0x4F, 0x43, 0x54, 0x59, 0x50, 0x45}, // <!DOCTYPE
            {0x3C, 0x68, 0x74, 0x6D, 0x6C},                         // <html
            {0x3C, 0x48, 0x54, 0x4D, 0x4C}                          // <HTML
    }),
    SQLITE("sqlite", new int[][]{
            {0x53, 0x51, 0x4C, 0x69, 0x74, 0x65, 0x20, 0x66, 0x6F, 0x72, 0x6D, 0x61, 0x74, 0x20, 0x33, 0x00} // SQLite format 3
    }),
    ISO("iso", new int[][]{
            {0x43, 0x44, 0x30, 0x30, 0x31} // CD001
    }),
    JAVA_CLASS("class", new int[][]{
            {0xCA, 0xFE, 0xBA, 0xBE}
    }),
    ZIP("zip", new int[][]{
            {0x50, 0x4B, 0x03, 0x04}, // 标准ZIP
            {0x50, 0x4B, 0x05, 0x06}, // 空ZIP
            {0x50, 0x4B, 0x07, 0x08}  // 跨磁盘ZIP
    });
    private final String extension;
    private final int[][] signatures;

    FileType(String extension, int[][] signatures) {
        this.extension = extension;
        this.signatures = signatures;
    }

    public String getExtension() {
        return extension;
    }

    public int[][] getSignatures() {
        return signatures;
    }

    /**
     * 根据文件头字节判断文件类型
     * @param fileHeader 文件头字节数组
     * @return 匹配的文件类型，未匹配返回TXT
     */
    public static FileType getFileType(byte[] fileHeader) {
        if (fileHeader == null || fileHeader.length == 0) {
            return null;
        }

        // 将byte数组转换为int数组（无符号处理）
        int[] headerInts = new int[fileHeader.length];
        for (int i = 0; i < fileHeader.length; i++) {
            headerInts[i] = fileHeader[i] & 0xFF; // 转换为无符号整数
        }
        return getFileTypeFromInts(headerInts);
    }

    /**
     * 根据int数组判断文件类型
     * @param headerInts 文件头int数组（无符号）
     * @return 匹配的文件类型，未匹配返回TXT
     */
    private static FileType getFileTypeFromInts(int[] headerInts) {
        for (FileType fileType : FileType.values()) {
            for (int[] signature : fileType.getSignatures()) {
                if (signature.length == 0) {
                    continue; // 跳过无固定文件头的类型（如TXT）
                }

                if (headerInts.length >= signature.length) {
                    boolean match = true;
                    for (int i = 0; i < signature.length; i++) {
                        if (headerInts[i] != signature[i]) {
                            match = false;
                            break;
                        }
                    }
                    if (match) {
                        return fileType;
                    }
                }
            }
        }
        return TXT;
    }

    /**
     * 根据文件头字节判断文件类型（宽松匹配）
     * @param fileHeader 文件头字节数组
     * @param minMatchLength 最小匹配长度
     * @return 匹配的文件类型，未匹配返回TXT
     */
    public static FileType getFileType(byte[] fileHeader, int minMatchLength) {
        if (fileHeader == null || fileHeader.length == 0) {
            return null;
        }

        // 将byte数组转换为int数组（无符号处理）
        int[] headerInts = new int[fileHeader.length];
        for (int i = 0; i < fileHeader.length; i++) {
            headerInts[i] = fileHeader[i] & 0xFF;
        }

        for (FileType fileType : FileType.values()) {
            for (int[] signature : fileType.getSignatures()) {
                if (signature.length == 0) {
                    continue;
                }

                int matchLength = Math.min(Math.min(headerInts.length, signature.length), minMatchLength);
                boolean match = true;
                for (int i = 0; i < matchLength; i++) {
                    if (headerInts[i] != signature[i]) {
                        match = false;
                        break;
                    }
                }
                if (match) {
                    return fileType;
                }
            }
        }
        return TXT;
    }



    /**
     * 获取文件类型的描述信息
     * @return 文件类型描述
     */
    public String getDescription() {
        switch (this) {
            case JPG: return "JPEG图像文件";
            case PNG: return "PNG图像文件";
            case GIF: return "GIF动画图像";
            case BMP: return "位图图像";
            case TIFF: return "TIFF图像";
            case WEBP: return "WebP图像";
            case PDF: return "PDF文档";
            case DOC: return "Word文档";
            case DOCX: return "Word文档 (2007+)";
            case XLSX: return "Excel文档 (2007+)";
            case PPTX: return "PowerPoint文档 (2007+)";
            case XLS: return "Excel文档 (97-2003)";
            case PPT: return "PowerPoint文档 (97-2003)";
            case RTF: return "富文本格式";
            case ZIP: return "ZIP压缩文件";
            case RAR: return "RAR压缩文件";
            case SEVEN_Z: return "7-Zip压缩文件";
            case GZIP: return "GZIP压缩文件";
            case TAR: return "TAR归档文件";
            case MP3: return "MP3音频文件";
            case WAV: return "WAV音频文件";
            case FLAC: return "FLAC音频文件";
            case OGG: return "OGG音频文件";
            case AAC: return "AAC音频文件";
            case MP4: return "MP4视频文件";
            case AVI: return "AVI视频文件";
            case MKV: return "Matroska视频文件";
            case FLV: return "Flash视频文件";
            case MOV: return "QuickTime视频";
            case EXE: return "Windows可执行文件";
            case ELF: return "Linux可执行文件";
            case MACH_O: return "macOS可执行文件";
            case TXT: return "文本文件";
            case XML: return "XML文档";
            case HTML: return "HTML网页";
            case SQLITE: return "SQLite数据库";
            case ISO: return "光盘映像";
            case JAVA_CLASS: return "Java类文件";
            default: return "未知文件类型";
        }
    }

    /**
     * 获取该文件类型的MIME类型
     * @return MIME类型字符串
     */
    public String getMimeType() {
        switch (this) {
            case JPG: return "image/jpeg";
            case PNG: return "image/png";
            case GIF: return "image/gif";
            case BMP: return "image/bmp";
            case TIFF: return "image/tiff";
            case WEBP: return "image/webp";
            case PDF: return "application/pdf";
            case DOC: return "application/msword";
            case DOCX: return "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
            case XLSX: return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
            case PPTX: return "application/vnd.openxmlformats-officedocument.presentationml.presentation";
            case RTF: return "application/rtf";
            case ZIP: return "application/zip";
            case RAR: return "application/vnd.rar";
            case SEVEN_Z: return "application/x-7z-compressed";
            case GZIP: return "application/gzip";
            case TAR: return "application/x-tar";
            case MP3: return "audio/mpeg";
            case WAV: return "audio/wav";
            case FLAC: return "audio/flac";
            case OGG: return "audio/ogg";
            case AAC: return "audio/aac";
            case MP4: return "video/mp4";
            case AVI: return "video/x-msvideo";
            case MKV: return "video/x-matroska";
            case FLV: return "video/x-flv";
            case MOV: return "video/quicktime";
            case EXE: return "application/x-msdownload";
            case ELF: return "application/x-executable";
            case MACH_O: return "application/x-mach-binary";
            case TXT: return "text/plain";
            case XML: return "application/xml";
            case HTML: return "text/html";
            case SQLITE: return "application/x-sqlite3";
            case ISO: return "application/x-iso9660-image";
            case JAVA_CLASS: return "application/java-vm";
            default: return "application/octet-stream";
        }
    }

    /**
     * 检查文件头是否匹配指定的文件类型
     * @param fileHeader 文件头字节数组
     * @param fileType 要检查的文件类型
     * @return 是否匹配
     */
    public static boolean isFileType(byte[] fileHeader, FileType fileType) {
        if (fileHeader == null || fileType == null) {
            return false;
        }

        // 将byte数组转换为int数组（无符号处理）
        int[] headerInts = new int[fileHeader.length];
        for (int i = 0; i < fileHeader.length; i++) {
            headerInts[i] = fileHeader[i] & 0xFF;
        }

        for (int[] signature : fileType.getSignatures()) {
            if (signature.length == 0) {
                continue;
            }

            if (headerInts.length >= signature.length) {
                boolean match = true;
                for (int i = 0; i < signature.length; i++) {
                    if (headerInts[i] != signature[i]) {
                        match = false;
                        break;
                    }
                }
                if (match) {
                    return true;
                }
            }
        }
        return false;
    }
    /**
     * 获取当前枚举类中所有签名所需的最大读取字节数
     * @return 最大读取字节数
     */
    public static int getMaxReadLength() {
        int maxLength = 0;

        for (FileType fileType : FileType.values()) {
            for (int[] signature : fileType.getSignatures()) {
                if (signature.length > maxLength) {
                    maxLength = signature.length;
                }
            }
        }

        return maxLength;
    }

    /**
     * 获取指定文件类型所需的最大读取字节数
     * @param fileType 文件类型
     * @return 该类型所需的最大读取字节数
     */
    public static int getMaxReadLength(FileType fileType) {
        if (fileType == null) {
            return 0;
        }

        int maxLength = 0;
        for (int[] signature : fileType.getSignatures()) {
            if (signature.length > maxLength) {
                maxLength = signature.length;
            }
        }

        return maxLength;
    }

    /**
     * 检查是否为图像文件
     * @return 是否为图像文件
     */
    public boolean isImage() {
        return this == JPG || this == PNG || this == GIF || this == BMP ||
                this == TIFF || this == WEBP;
    }

    /**
     * 检查是否为文档文件
     * @return 是否为文档文件
     */
    public boolean isDocument() {
        return this == PDF || this == DOC || this == DOCX || this == XLS || this == XLSX ||
                this == PPT || this == PPTX || this == RTF || this == TXT || this == XML ||
                this == HTML || this == ODT || this == ODS;
    }

    /**
     * 检查是否为压缩文件
     * @return 是否为压缩文件
     */
    public boolean isArchive() {
        return this == ZIP || this == RAR || this == SEVEN_Z || this == GZIP ||
                this == TAR;
    }

    /**
     * 检查是否为音频文件
     * @return 是否为音频文件
     */
    public boolean isAudio() {
        return this == MP3 || this == WAV || this == FLAC || this == OGG ||
                this == AAC;
    }

    /**
     * 检查是否为视频文件
     * @return 是否为视频文件
     */
    public boolean isVideo() {
        return this == MP4 || this == AVI || this == MKV || this == FLV ||
                this == MOV;
    }

    /**
     * 检查是否为可执行文件
     * @return 是否为可执行文件
     */
    public boolean isExecutable() {
        return this == EXE || this == ELF || this == MACH_O || this == JAVA_CLASS;
    }
    public boolean isOfficeDocument() {
        return this == DOC || this == DOCX || this == XLS || this == XLSX ||
                this == PPT || this == PPTX;
    }

    public boolean isModernOffice() {
        return this == DOCX || this == XLSX || this == PPTX;
    }

    public boolean isLegacyOffice() {
        return this == DOC || this == XLS || this == PPT;
    }
    /**
     * 获取文件类型的分类
     * @return 分类字符串
     */
    public static FileType deepCheckZipType(byte[] fileData) throws UnsupportedEncodingException {
        if (fileData == null || fileData.length < 100) {
            return ZIP;
        }

        // 转换为字符串以便搜索
        String dataStr = new String(fileData, "ISO_8859_1");

        // 检查Office文档
        if (dataStr.contains("[Content_Types].xml")) {
            // 进一步检查具体类型
            if (dataStr.contains("word/")) {
                return DOCX;
            } else if (dataStr.contains("xl/")) {
                return XLSX;
            } else if (dataStr.contains("ppt/")) {
                return PPTX;
            }
        }

        // 检查DOCX - 包含word/document.xml
        if (dataStr.contains("word/document.xml") || dataStr.contains("word/_rels/")) {
            return DOCX;
        }

        // 检查XLSX - 包含xl/workbook.xml
        if (dataStr.contains("xl/workbook.xml") || dataStr.contains("xl/worksheets/")) {
            return XLSX;
        }

        // 检查PPTX - 包含ppt/presentation.xml
        if (dataStr.contains("ppt/presentation.xml") || dataStr.contains("ppt/slides/")) {
            return PPTX;
        }

        // 检查APK - 包含AndroidManifest.xml
        if (dataStr.contains("AndroidManifest.xml")) {
            return APK;
        }

        // 检查JAR - 包含META-INF/
        if (dataStr.contains("META-INF/")) {
            return JAR;
        }

        // 检查WAR - 包含WEB-INF/
        if (dataStr.contains("WEB-INF/")) {
            return WAR;
        }

        // 检查EPUB - 包含mimetype application/epub+zip
        if (dataStr.contains("application/epub+zip")) {
            return EPUB;
        }

        // 检查ODT/ODS - OpenDocument格式
        if (dataStr.contains("application/vnd.oasis.opendocument")) {
            if (dataStr.contains("text")) {
                return ODT;
            } else if (dataStr.contains("spreadsheet")) {
                return ODS;
            }
        }

        // 检查IPA - 包含Payload/目录
        if (dataStr.contains("Payload/")) {
            return IPA;
        }

        // 检查AAB - 包含base/manifest
        if (dataStr.contains("base/manifest") || dataStr.contains("BundleConfig.pb")) {
            return AAB;
        }

        return ZIP;
    }
    public String getCategory() {
        if (isImage()) return "图像";
        if(isLegacyOffice()) return "(旧)Office文档";
        if (isOfficeDocument()) return "Office文档";
        if (isDocument()) return "文档";
        if (isArchive()) return "压缩文件";
        if (isAudio()) return "音频";
        if (isVideo()) return "视频";
        if (isExecutable()) return "可执行文件";
        if (this == SQLITE) return "数据库";
        if (this == ISO) return "光盘映像";
        return "其他";
    }
}
