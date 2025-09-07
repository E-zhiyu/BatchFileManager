package InterfaceFunction.Total;

import org.json.JSONArray;
import org.json.JSONTokener;

import java.io.*;

public class JsonReader {
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
     * 从文件中读取JSON数据
     *
     * @param targetFilePath 待读取的目标文件路径
     * @return 读取到的JSON数据
     */
    public JSONArray readJsonFile(String targetFilePath) {
        JSONArray jsonData;

        try (FileReader fileReader = new FileReader(targetFilePath)) {
            JSONTokener tokener = new JSONTokener(fileReader);
            jsonData = new JSONArray(tokener);
        } catch (IOException e) {
            jsonData = new JSONArray();
        }

        return jsonData;
    }

    /**
     * 发送读取到的JSON数据
     *
     * @param jsonData 待发送的JSON数据
     */
    public void sendData(JSONArray jsonData) {
        System.out.println(jsonData.toString());
    }

    /**
     * 发送运行结果标识符
     *
     * @param flag 运行结果标识符
     */
    public void sendFlag(int flag) {
        System.out.println(flag);
    }

    public static void main(String[] args) {
        String targetFilePath;
        JSONArray jsonData;
        JsonReader jsonReader = new JsonReader();

        targetFilePath = jsonReader.setTargetFilePath();
        if (!new File(targetFilePath).isFile()) {
            jsonReader.sendFlag(-1);
        }

        jsonData = jsonReader.readJsonFile(targetFilePath);
        if (jsonData.isEmpty()) {
            jsonReader.sendFlag(0);
        } else {
            jsonReader.sendData(jsonData);
        }
    }
}
