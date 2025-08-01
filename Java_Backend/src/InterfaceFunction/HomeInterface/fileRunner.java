package InterfaceFunction.HomeInterface;

import PythonConnector.GrandProcessConnector;
import org.json.JSONArray;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;

public class fileRunner implements GrandProcessConnector<String, Integer> {
    String fileToRun;
    Integer isRunningSuccess;

    /**
     * @return 从主进程获取到的文件路径列表
     */
    @Override
    public String receiveData() {
        String fileToRun = "";
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        //解析json数据
        try {
            String jsonInput = br.readLine();
            JSONArray ja = new JSONArray(jsonInput);

            for (int i = 0; i < ja.length(); i++) {
                fileToRun = ja.getString(i);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        return fileToRun;
    }

    /**
     * @param flag 成功运行与运行失败的文件数
     */
    @Override
    public void sendData(Integer flag) {
        List<Integer> l = new ArrayList<>();
        l.add(flag);

        JSONArray jsonArray = new JSONArray(l);
        System.out.println(jsonArray);
    }

    /**
     * 批量运行文件
     *
     * @param fileToRun 待运行文件的路径列表
     * @return 成功运行与运行失败的文件数
     */
    Integer runFiles(String fileToRun) throws IOException {
        int isRunningSuccess = 0;

        //创建与主进程（客户端）的连接
        ServerSocket serverSocket = new ServerSocket(8080);
        Socket clientSocket = serverSocket.accept();
        PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
        BufferedReader in = new BufferedReader(
                new InputStreamReader(clientSocket.getInputStream()));

        //创建文件运行进程
        File file = new File(fileToRun);
        ProcessBuilder builder = new ProcessBuilder("cmd", "/c", file.getAbsolutePath());

        builder.directory(file.getParentFile());  //设置工作目录
        builder.redirectErrorStream(true);  // 合并错误流

        //创建并启动进程
        try {
            Process process = builder.start();

            // 读取进程输出并发送到客户端
            new Thread(() -> {
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(process.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        out.println(line);
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }).start();

            // 从客户端读取命令并写入进程
            new Thread(() -> {
                try (BufferedWriter writer = new BufferedWriter(
                        new OutputStreamWriter(process.getOutputStream()))) {
                    String command;
                    while ((command = in.readLine()) != null && !command.isEmpty()) {
                        writer.write(command);
                        writer.newLine();
                        writer.flush();
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }).start();

        } catch (IOException e) {
            throw new IOException();
        }

        isRunningSuccess = 1;
        return isRunningSuccess;
    }

    public static void main(String[] args) {
        fileRunner fileRunner = new fileRunner();
        fileRunner.fileToRun = fileRunner.receiveData();
        try {
            fileRunner.isRunningSuccess = fileRunner.runFiles(fileRunner.fileToRun);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        //主进程读取数据的时候出错，所以暂时禁用
//        fileRunner.sendData(fileRunner.isRunningSuccess);
    }
}
