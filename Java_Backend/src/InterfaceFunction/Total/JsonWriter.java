package InterfaceFunction.Total;

import org.json.JSONArray;

import java.io.*;

public class JsonWriter {
    /**
     * 设置目标文件路径
     */
    public String setTargetFilePath() {
        String targetFilePath;

        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        try {
            JSONArray jsonData = new JSONArray(reader.readLine());
            targetFilePath = String.valueOf(jsonData.get(0));
        } catch (IOException e) {
            targetFilePath = "";
        }

        return targetFilePath;
    }

    /**
     * 从标准输入获取JSON数据
     *
     * @return 生成的JSON数组
     */
    public JSONArray receiveData() {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        JSONArray jsonArray;

        try {
            jsonArray = new JSONArray(reader.readLine());
        } catch (IOException e) {
            jsonArray = null;
        }

        return jsonArray;
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
        try (FileWriter fileWriter = new FileWriter(targetFilePath)) {
            fileWriter.write(data.toString(4));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public static void main(String[] args) {
        JsonWriter jsonWriter = new JsonWriter();
        String targetFilePath;
        JSONArray jsonData;

        targetFilePath = jsonWriter.setTargetFilePath();
        if (targetFilePath.isEmpty()) {
            jsonWriter.sendFlag(0);
            return;
        }

        jsonData = jsonWriter.receiveData();
        if (jsonData == null) {
            jsonWriter.sendFlag(0);
            return;
        }

        try {
            jsonWriter.writeData(targetFilePath, jsonData);
        } catch (RuntimeException e) {
            jsonWriter.sendFlag(0);
            return;
        }

        jsonWriter.sendFlag(1);
    }
}
