package InterfaceFunction.Total;

import org.json.JSONArray;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class JsonWriter {
    /**
     * 从标准输入获取JSON数据
     *
     * @return 生成的JSON数组
     */
    public JSONArray receiveData() {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        JSONArray jsonData;

        try {
            jsonData = new JSONArray(reader.readLine());
        } catch (IOException e) {
            jsonData = new JSONArray();
        }

        return jsonData;
    }

    /**
     * 发送运行结果标识符
     *
     * @param flag 运行结果标识符
     */
    public void sendFlag(int flag) {
        System.out.println(flag);
    }

    /**
     * 将JSON数组写入文件
     *
     * @param data 需要写入的JSON数组
     */
    public void writeData(String targetFilePath, JSONArray data) {
        Path targetPath = Paths.get(targetFilePath);
        Path parentDir = targetPath.getParent();
        
        try {
            //生成父文件夹
            Files.createDirectories(parentDir);

            //创建文件并将数据写入文件
            try (FileWriter fileWriter = new FileWriter(targetFilePath)) {
                fileWriter.write(data.toString(4));
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }


    }

    public static void main(String[] args) {
        JsonWriter jsonWriter = new JsonWriter();
        String targetFilePath;
        JSONArray jsonData, inputData;

        jsonData = jsonWriter.receiveData();
        if (jsonData.isEmpty()) {
            jsonWriter.sendFlag(0);
            return;
        }

        //分离目标文件路径和待写入的数据
        targetFilePath = jsonData.get(0).toString();
        inputData = (JSONArray) jsonData.get(1);

        try {
            jsonWriter.writeData(targetFilePath, inputData);
        } catch (RuntimeException e) {
            jsonWriter.sendFlag(0);
            return;
        }

        jsonWriter.sendFlag(1);
    }
}
