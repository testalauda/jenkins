public class CommonController extends BaseController {  
    Log log = LogFactory.getLog(CommonController.class);  
      
    Properties fileUploadPro = null;  
    public CommonController(){  
        fileUploadPro = PropertiesUtil.getPropertiesByClass("fileupload.properties");  
    }  
      
      
    @Override  
    public ModeAndView init(HttpServletRequest request,  
            HttpServletResponse response) throws ServletException, IOException {  
          
        return null;  
    }  
      
    /** 
     * 跳转到文件上传页 
     * @param request 
     * @param response 
     * @return 
     * @throws ServletException 
     * @throws IOException 
     */  
    public ModeAndView goFileUpload(HttpServletRequest request,  
            HttpServletResponse response) throws ServletException, IOException {  
        String functionId = request.getParameter("functionId");  
        String fileType = request.getParameter("fileType");  
        String maxSize = request.getParameter("maxSize");  
        ModeAndView mav = new ModeAndView("/WEB-INF/jsp/common/fileUpload.jsp");  
          
        if(functionId!=null && !"".equals(functionId.trim())){  
            mav.addObject("functionId", functionId);  
        }  
        if(fileType!=null && !"".equals(fileType.trim())){  
            mav.addObject("fileType", fileType);  
        }  
        if(maxSize!=null && !"".equals(maxSize.trim())){  
            mav.addObject("maxSize", maxSize);  
        }  
        return mav;  
    }  
      
    /** 
     * 上传文件 
     * @param request 
     * @param response 
     * @return 
     * @throws ServletException 
     * @throws IOException 
     */  
    @SuppressWarnings("unchecked")  
    public ModeAndView doFileUpload(HttpServletRequest request,  
            HttpServletResponse response) throws ServletException, IOException {  
        //获取并解析文件类型和支持最大值  
        String functionId = request.getParameter("functionId");  
        String fileType = request.getParameter("fileType");  
        String maxSize = request.getParameter("maxSize");  
          
        //临时目录名  
        String tempPath = fileUploadPro.getProperty("tempPath");  
        //真实目录名  
        String filePath = fileUploadPro.getProperty("filePath");  
          
        FileUtil.createFolder(tempPath);  
        FileUtil.createFolder(filePath);  
          
        DiskFileItemFactory factory = new DiskFileItemFactory();  
        //最大缓存  
        factory.setSizeThreshold(5*1024);  
        //设置临时文件目录  
        factory.setRepository(new File(tempPath));  
        ServletFileUpload upload = new ServletFileUpload(factory);  
        if(maxSize!=null && !"".equals(maxSize.trim())){  
            //文件最大上限  
            upload.setSizeMax(Integer.valueOf(maxSize)*1024*1024);  
        }  
          
        try {  
            //获取所有文件列表  
            List<FileItem> items = upload.parseRequest(request);  
            for (FileItem item : items) {  
                if(!item.isFormField()){  
                    //文件名  
                    String fileName = item.getName();  
                      
                    //检查文件后缀格式  
                    String fileEnd = fileName.substring(fileName.lastIndexOf(".")+1).toLowerCase();  
                    if(fileType!=null && !"".equals(fileType.trim())){  
                        boolean isRealType = false;  
                        String[] arrType = fileType.split(",");  
                        for (String str : arrType) {  
                            if(fileEnd.equals(str.toLowerCase())){  
                                isRealType = true;  
                                break;  
                            }  
                        }  
                        if(!isRealType){  
                            //提示错误信息:文件格式不正确  
                            super.printJsMsgBack(response, "文件格式不正确!");  
                            return null;  
                        }  
                    }  
                      
                    //创建文件唯一名称  
                    String uuid = UUID.randomUUID().toString();  
                    //真实上传路径  
                    StringBuffer sbRealPath = new StringBuffer();  
                    sbRealPath.append(filePath).append(uuid).append(".").append(fileEnd);  
                    //写入文件  
                    File file = new File(sbRealPath.toString());  
                    item.write(file);  
                    //上传成功，向父窗体返回数据:真实文件名,虚拟文件名,文件大小  
                    StringBuffer sb = new StringBuffer();  
                    sb.append("window.returnValue='").append(fileName).append(",").append(uuid).append(".").append(fileEnd).append(",").append(file.length()).append("';");  
                    sb.append("window.close();");  
                    super.printJsMsg(response, sb.toString());  
                    log.info("上传文件成功,JS信息："+sb.toString());  
                }//end of if  
            }//end of for  
              
        }catch (Exception e) {  
            //提示错误:比如文件大小  
            super.printJsMsgBack(response, "上传失败,文件大小不能超过"+maxSize+"M!");  
            log.error("上传文件异常!",e);  
            return null;  
        }  
          
        return null;  
    }  
} 
