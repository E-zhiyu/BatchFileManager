package InterfaceFunction.HomeInterface;

import org.json.JSONArray;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.ArrayList;
import java.util.List;

import PythonConnector.GrandProcessConnector;


public class FileAdder implements GrandProcessConnector<List<String>, List<List<String>>> {
    static List<String> filePaths;
    static List<List<String>> allFileInfos;

    /**
     * 从标准输入接收文件路径列表
     *
     * @return 接收到的文件路径列表
     */
    @Override
    public List<String> receiveData() {
        // 读取标准输入
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        List<String> allFilePaths = new ArrayList<>();

        try {
            String jsonInput = reader.readLine();  // 读取一行JSON数据
            JSONArray jsonArray = new JSONArray(jsonInput);  // 解析JSON

            // 转换为Java List
            for (int i = 0; i < jsonArray.length(); i++) {
                allFilePaths.add(String.valueOf(jsonArray.get(i)));
            }
        } catch (IOException e) {  //读取标准输入时的异常处理
            List<String> l = new ArrayList<>();  //发送空的列表
            JSONArray jsonArray = new JSONArray(l);
            System.out.println(jsonArray);
        }

        return allFilePaths;
    }


    /**
     * 发送获取到的文件信息
     *
     * @param fileInfos 需要发送的文件信息列表
     */
    @Override
    public void sendData(List<List<String>> fileInfos) {
        JSONArray jsonArray = new JSONArray(fileInfos);
        System.out.println(jsonArray);
    }

    /**
     * 获取文件信息
     *
     * @param filePaths 文件路径列表
     * @return 获取到的文件信息列表
     */
    private List<List<String>> getFileInfos(List<String> filePaths) {
        List<List<String>> allFileInfos = new ArrayList<>();

        for (String onePath : filePaths) {
            Path path = Paths.get(onePath);

            String fileName = path.getFileName().toString();  //获取文件名（带后缀）
            String date = null;
            String extension = fileName.substring(fileName.lastIndexOf(".") + 1);  //获取后缀名
            String fileSize = null;

            try {
                BasicFileAttributes attrs = Files.readAttributes(path, BasicFileAttributes.class);  //获取文件属性对象

                //获取修改日期
                long lastModified = attrs.lastModifiedTime().toMillis();
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
                date = sdf.format(new Date(lastModified));

                //获取文件大小
                long size = attrs.size();
                if (size < 1024) {
                    fileSize = size + "B";
                } else if (size < 1024 * 1024) {
                    fileSize = size + "KB";
                } else if (size < 1024 * 1024 * 1024) {
                    fileSize = size + "MB";
                } else {
                    fileSize = size + "GB";
                }
            } catch (IOException e) {
                date = "未知";
                fileSize = "未知";
            } finally {
                //将文件信息打包
                List<String> oneFileInfos = new ArrayList<>();
                oneFileInfos.add(fileName);
                oneFileInfos.add(date);
                oneFileInfos.add(extension);
                oneFileInfos.add(fileSize);
                allFileInfos.add(oneFileInfos);
            }
        }

        return allFileInfos;
    }

    public static void main(String[] args) {
        FileAdder fileAdder = new FileAdder();
        filePaths = fileAdder.receiveData();
        if (!filePaths.isEmpty()) {
            allFileInfos = fileAdder.getFileInfos(filePaths);
            fileAdder.sendData(allFileInfos);
        }
    }
}
