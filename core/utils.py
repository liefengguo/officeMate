import hashlib
import chardet

def get_file_hash(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("get_file_hash 只接受 str 类型内容，请先解码字节数据。")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def read_file_content(file_path: str) -> str:
    """读取文件内容并返回文本"""
    with open(file_path, "rb") as file:  # 以二进制模式读取文件
        raw_data = file.read()
        result = chardet.detect(raw_data)  # 自动检测编码
        encoding = result['encoding']
        if encoding is None:
            encoding = 'utf-8'
        
        try:
            return raw_data.decode(encoding)  # 尝试使用检测到的编码解码
        except (UnicodeDecodeError):
            for fallback_encoding in ['gbk', 'big5', 'latin1']:
                try:
                    return raw_data.decode(fallback_encoding)  # 尝试 fallback 编码
                except UnicodeDecodeError:
                    continue
            raise UnicodeDecodeError("所有编码解码尝试均失败。")

    return ""  # 如果读取失败，返回空字符串（虽然这个代码路径不会被执行）
