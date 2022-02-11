from django import template
import os
import mimetypes

register = template.Library()

additional_file_types = {
    '.md': 'markdown',
    '.txt': 'plain',
    '.html': 'html',
    '.css': 'css',
    '.js': 'javascript',
    '.PNG': 'png',
    '.jpg': 'jpeg',
    '.jpeg': 'jpeg',
    '.gif': 'gif',
    '.png': 'png',
    '.mp3': 'mpeg',
    '.wav': 'wav',
    '.ogg': 'ogg',
    '.mp4': 'mp4',
    '.webm': 'webm',
    '.ogv': 'ogg',
    '.mov': 'quicktime',
    '.avi': 'avi',
    '.wmv': 'wmv',
    '.flv': 'flv',
    '.swf': 'flash',
    '.mpg': 'mpeg',
    '.mpeg': 'mpeg',
    '.mp4': 'mp4',
    '.m4v': 'mp4',
    '.m4a': 'mp4',
    '.m4b': 'mp4',
    '.m4p': 'mp4',
    '.m4r': 'mp4',
    '.m4v': 'mp4',
    '.mov': 'video',
    '.pdf': 'pdf',
    '.doc': 'doc',
    '.docx': 'doc',
    '.xls': 'excel',
    '.xlsx': 'excel',
    '.ppt': 'powerpoint',
    '.pptx': 'powerpoint',
    '.odt': 'text',
    '.py': 'python',
    '.rb': 'ruby',
    '.sh': 'bash',
    '.c': 'c',
    '.cpp': 'c',
    '.h': 'c',
    '.hpp': 'c',
    '.hxx': 'c',
    '.h++': 'c',
    '.cs': 'csharp',
    '.java': 'java',
    '.php': 'php',
    '.pl': 'perl',
    '.sql': 'sql',
    '.xml': 'xml',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.ini': 'ini',
    '.json': 'json',
    '.log': 'log',
    '.db': 'sql',
    '.sqlite': 'sqlite',
    '.sqlite3': 'sqlite',
    '.db3': 'sqlite',
}

@register.filter
def file_type(key):
    file_info = os.path.splitext(key)
    file_extension = file_info[1]
    try:
        if(file_extension == '.enc'):
            filetype = 'Encrypted File'
            return filetype
        if(file_extension in additional_file_types.keys()):
            filetype = additional_file_types[file_extension]
            return filetype
        else:
            filetype = mimetypes.guess_type(key)[0]
            return filetype
    except KeyError:
        filetype = 'Unknown'
        if(file_info[0].startswith('.') and file_extension == ''):
            filetype = 'text'
        if(file_extension in additional_file_types.keys()):
            filetype = additional_file_types[file_extension]

        return filetype