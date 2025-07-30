package InterfaceFunction.HomeInterface;

import PythonConnector.GrandProcessConnector;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class fileRunner implements GrandProcessConnector<List<String>, List<Integer>> {
    List<String> filesToRun;
    List<Integer> successAndFailed;

    /**
     * @return 从主进程获取到的文件路径列表
     */
    @Override
    public List<String> receiveData() {
        List<String> filesToRun = new ArrayList<>();
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        //解析json数据
        try {
            String jsonInput = br.readLine();
            JSONArray ja = new JSONArray(jsonInput);

            for (int i = 0; i < ja.length(); i++) {
                filesToRun.add(ja.getString(i));
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        return filesToRun;
    }

    /**
     * @param flag 成功运行与运行失败的文件数
     */
    @Override
    public void sendData(List<Integer> flag) {
        JSONArray jsonArray = new JSONArray(flag.toString());
        System.out.println(jsonArray);
    }

    /**
     * 批量运行文件
     *
     * @param filesToRun 待运行文件的路径列表
     * @return 成功运行与运行失败的文件数
     */
    List<Integer> runFiles(List<String> filesToRun) {
        int success = 0;
        int failed = 0;

        for (String filePath : filesToRun) {
            File file = new File(filePath);
            ProcessBuilder builder = new ProcessBuilder("cmd", "/c", "start", filePath);

            //设置工作目录
            builder.directory(file.getParentFile());

            // 合并错误流
            builder.redirectErrorStream(true);

            //创建并启动进程
            try {
                Process process = builder.start();

                // 读取输出
//                BufferedReader reader = new BufferedReader(
//                        new InputStreamReader(process.getInputStream()));
//                String line;
//                while ((line = reader.readLine()) != null) {
//                    JSONObject jo = new JSONObject(line);
//                    System.out.println(jo);
//                }

                //成功文件数加一
                success++;
            } catch (IOException e) {
                failed++;
            }
        }

        List<Integer> successAndFailed = new ArrayList<>();
        successAndFailed.add(success);
        successAndFailed.add(failed);
        return successAndFailed;
    }

    public static void main(String[] args) {
        fileRunner fileRunner = new fileRunner();
        fileRunner.filesToRun = fileRunner.receiveData();
        fileRunner.successAndFailed = fileRunner.runFiles(fileRunner.filesToRun);
        fileRunner.sendData(fileRunner.successAndFailed);
    }
}
