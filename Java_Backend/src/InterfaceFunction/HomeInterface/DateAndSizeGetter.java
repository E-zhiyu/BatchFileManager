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
import java.util.ArrayList;
import java.util.List;

import PythonConnector.GrandProcessConnector;


public class DateAndSizeGetter implements GrandProcessConnector<List<String>, List<List<String>>> {
    @Override
    public List<String> receiveData() {
        List<String> filePaths = new ArrayList<>();
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
        String inputLine;
        JSONArray inputJsonData;

        try {
            //读取JSON数据
            inputLine = in.readLine();
            inputJsonData = new JSONArray(inputLine);
        } catch (IOException e) {  //处理读取错误的异常
            List<String> emptyList = new ArrayList<>();
            JSONArray emptyJsonArray = new JSONArray(emptyList);
            System.out.println(emptyJsonArray);
            return filePaths;  //返回空列表
        }

        //解析JSON数据
        for (int i = 0; i < inputJsonData.length(); i++) {
            String path = String.valueOf(inputJsonData.get(i));
            filePaths.add(path);
        }

        return filePaths;
    }

    @Override
    public void sendData(List<List<String>> data) {
        JSONArray jsonArray = new JSONArray(data);
        System.out.println(jsonArray);
    }

    public List<List<String>> getDateAndSize(List<String> filePaths) {
        List<List<String>> dateAndSize = new ArrayList<>();

        for (String filePath : filePaths) {
            Path path = Paths.get(filePath);
            String size, date;
            size = date = "未知";
            try {
                BasicFileAttributes attr = Files.readAttributes(path, BasicFileAttributes.class);

                long diff = attr.lastModifiedTime().toMillis();
                SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd");
                date = formatter.format(diff);

                long file_size = attr.size();
                if (file_size < 1024) {
                    size = file_size + "B";
                } else if (file_size < 1024 * 1024) {
                    size = file_size + "KB";
                } else if (file_size < 1024 * 1024 * 1024) {
                    size = file_size + "MB";
                } else {
                    size = file_size + "GB";
                }
            } catch (IOException e) {
                size = date = "未知";
            } finally {
                List<String> oneFileInfo = new ArrayList<>();
                oneFileInfo.add(date);
                oneFileInfo.add(size);
                dateAndSize.add(oneFileInfo);
            }
        }

        return dateAndSize;
    }

    public static void main(String[] args) {
        DateAndSizeGetter dateAndSizeGetter = new DateAndSizeGetter();
        List<String> filePaths = dateAndSizeGetter.receiveData();
        if (!filePaths.isEmpty()) {
            List<List<String>> dateAndSize = dateAndSizeGetter.getDateAndSize(filePaths);
            dateAndSizeGetter.sendData(dateAndSize);
        }
    }
}
