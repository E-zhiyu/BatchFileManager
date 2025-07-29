package InterfaceFunction.HomeInterface;

import org.json.JSONArray;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.ArrayList;
import java.util.List;


public class FileAdder {
    static List<String> filePaths;
    static List<List<String>> fileInfos;

    /**
     * 从标准输入接收文件路径列表
     *
     * @return 接收到的文件路径列表
     */
    static private List<String> receiveData() {
        // 读取标准输入
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));

        List<String> allFilePaths = new ArrayList<>();
        try {
            String jsonInput = reader.readLine();  // 读取一行JSON数据

            // 解析JSON
            JSONArray jsonArray = new JSONArray(jsonInput);

            // 转换为Java List
            for (int i = 0; i < jsonArray.length(); i++) {
                allFilePaths.add(String.valueOf(jsonArray.get(i)));
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        return allFilePaths;
    }

    /**
     * 获取文件信息
     *
     * @param filePaths 文件路径列表
     * @return 获取到的文件信息列表
     */
    static private List<List<String>> getFileInfos(List<String> filePaths) {
        List<List<String>> allFileInfos = new ArrayList<>();

        for (String onePath : filePaths) {
            Path path = Paths.get(onePath);

            //获取文件名（带后缀）
            String fileName = path.getFileName().toString();

            //获取修改日期
            BasicFileAttributes attrs = null;
            String date = "未知";
            try {
                attrs = Files.readAttributes(path, BasicFileAttributes.class);
                long lastModified = attrs.lastModifiedTime().toMillis();
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
                date = sdf.format(new Date(lastModified));
            } catch (IOException _) {
            }

            //获取后缀名
            String extension = fileName.substring(fileName.lastIndexOf(".") + 1);

            //获取文件大小
            String fileSize = "未知";
            if (attrs != null) {
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
            }

            //将文件信息打包
            List<String> oneFileInfos = new ArrayList<>();
            oneFileInfos.add(fileName);
            oneFileInfos.add(date);
            oneFileInfos.add(extension);
            oneFileInfos.add(fileSize);
            allFileInfos.add(oneFileInfos);
        }

        return allFileInfos;
    }

    /**
     * 发送获取到的文件信息
     *
     * @param fileInfos 需要发送的文件信息列表
     */
    static private void sendInfos(List<List<String>> fileInfos) {
        JSONArray jsonArray = new JSONArray(fileInfos);
        System.out.println(jsonArray + "\n");
    }

    public static void main(String[] args) {
        filePaths = receiveData();
        fileInfos = getFileInfos(filePaths);
        sendInfos(fileInfos);
    }
}
