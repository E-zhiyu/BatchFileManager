package InterfaceFunction.HomeInterface;

import PythonConnector.GrandProcessConnector;
import org.json.JSONArray;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class fileRunner implements GrandProcessConnector<String, Boolean> {
    static String fileToRun;

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
            this.sendData(false);  //Python端消息接收失败异常处理
            fileToRun = "";
        }

        return fileToRun;
    }

    @Override
    public void sendData(Boolean data) {
        List<Boolean> l = new ArrayList<>();
        l.add(data);

        JSONArray jsonArray = new JSONArray(l);
        System.out.println(jsonArray);
    }

    /**
     * 强制结束文件运行进程
     *
     * @param process 需要结束的进程
     */
    void killProcess(Process process) {
        process.destroy();
        if (process.isAlive()) {
            process.destroyForcibly();
        }
    }

    /**
     * 运行文件
     *
     * @param fileToRun 待运行文件的路径列表
     */
    void runFile(String fileToRun) {
        int exitCode = -1;

        //创建与主进程（客户端）的连接
        try (ServerSocket serverSocket = new ServerSocket(1918)) {
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
            Process process = builder.start();

            // 启动读取进程输出并发送到客户端
            new Thread(() -> {
                try (InputStream is = process.getInputStream();
                     InputStreamReader isr = new InputStreamReader(is, "GBK");
                     BufferedReader br = new BufferedReader(isr)) {
                    String line;
                    while ((line = br.readLine()) != null) {
                        out.println(line);
                        out.flush();
                    }
                } catch (IOException e) {  //读出内容时的异常处理
                    out.println("[ERROR] " + e.getMessage());
                }
            }).start();

            // 启动从客户端读取命令并写入进程
            new Thread(() -> {
                try (BufferedWriter writer = new BufferedWriter(
                        new OutputStreamWriter(process.getOutputStream(), StandardCharsets.UTF_8))) {
                    String command;
                    while ((command = in.readLine()) != null) {
                        //判断是否为终止进程命令
                        if (command.startsWith("#") && command.endsWith("#")) {
                            killProcess(process);
                            break;
                        }

                        writer.write(command);
                        writer.newLine();
                        writer.flush();
                    }
                } catch (IOException e) {  //写入命令时的异常处理
                    out.println("[ERROR] " + e.getMessage());
                }
            }).start();

            try {
                exitCode = process.waitFor();
                out.println("#进程已退出，代码：" + exitCode);
                out.flush();
            } catch (InterruptedException e) {  //获取返回值时的异常处理
                Thread.currentThread().interrupt();
                out.println("[ERROR] 执行被中断");
                out.flush();
            }
        } catch (IOException _) {  //创建套接字时的异常处理
            //Python主进程已处理无法连接至套接字的情况，此处无需异常处理，直接结束进程即可
        }
    }

    public static void main(String[] args) {
        fileRunner fileRunner = new fileRunner();
        fileToRun = fileRunner.receiveData();
        if (!fileToRun.isEmpty()) {
            fileRunner.sendData(true);  //成功接收文件路径则返回1
            fileRunner.runFile(fileToRun);
        }
    }
}
