/// <summary> 
/// C#文件下载 
/// </summary> 
/// <param name="filename"></param> 
public void MyDownload(string filename) 
{ 
  
  string path = ServerMapPath("/File/"+filename); 
  if(!FileExists(path)) 
  { 
    ResponseWrite("对不起！文件不存在！！"); 
    return; 
  } 
  SystemIOFileInfo file = new SystemIOFileInfo(path); 
  string fileFilt="asp|aspx|php|jsp|ascx|config|asa|"; //不可下载的文件，务必要过滤干净 
  string fileName = fileName; 
  string fileExt = fileNameSubstring(filenameLastIndexOf(""))Trim()ToLower(); 
  if(fileFiltIndexOf(fileExt)!=-1) 
  { 
    ResponseWrite("对不起！该类文件禁止下载！！"); 
  } 
  else
  { 
    ResponseClear(); 
    ResponseAddHeader("Content-Disposition", "attachment; filename=" + HttpUtilityUrlEncode(fileName)); 
    ResponseAddHeader("Content-Length", fileLengthToString()); 
    ResponseContentType = GetContentType(HttpUtilityUrlEncode(fileExt)); 
    ResponseWriteFile(fileFullName); 
    ResponseEnd(); 
  } 
} 
  
/// <summary> 
/// 获取下载类型 
/// </summary> 
/// <param name="fileExt"></param> 
/// <returns></returns> 
public string GetContentType(string fileExt) 
{ 
  string ContentType; 
  switch (fileExt) 
  { 
    case "asf": 
      ContentType = "video/x-ms-asf"; break; 
    case "avi": 
      ContentType = "video/avi"; break; 
    case "doc": 
      ContentType = "application/msword"; break; 
    case "zip": 
      ContentType = "application/zip"; break; 
    case "xls": 
      ContentType = "application/vndms-excel"; break; 
    case "gif": 
      ContentType = "image/gif"; break; 
    case "jpg": 
      ContentType = "image/jpeg"; break; 
    case "jpeg": 
      ContentType = "image/jpeg"; break; 
    case "wav": 
      ContentType = "audio/wav"; break; 
    case "mp3": 
      ContentType = "audio/mpeg3"; break; 
    case "mpg": 
      ContentType = "video/mpeg"; break; 
    case "mepg": 
      ContentType = "video/mpeg"; break; 
    case "rtf": 
      ContentType = "application/rtf"; break; 
    case "html": 
      ContentType = "text/html"; break; 
    case "htm": 
      ContentType = "text/html"; break; 
    case "txt": 
      ContentType = "text/plain"; break; 
    default: 
      ContentType = "application/octet-stream"; 
      break; 
  } 
  return ContentType; 
}
