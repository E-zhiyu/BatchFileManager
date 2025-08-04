package InterfaceFunction.HomeInterface;

import PythonConnector.GrandProcessConnector;
import org.json.JSONArray;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;

public class fileRunner implements GrandProcessConnector<String, Integer> {
    String fileToRun;

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

    @Override
    public void sendData(Integer data) {
//        List<Integer> l = new ArrayList<>();
//        l.add(data);
//
//        JSONArray jsonArray = new JSONArray(l);
//        System.out.println(jsonArray);
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

        if (process.isAlive()) {
            // 获取进程PID
            long pid = process.pid();

            // Windows系统
            if (System.getProperty("os.name").toLowerCase().contains("win")) {
                try {
                    Runtime.getRuntime().exec("taskkill /F /PID " + pid);
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }
        }
    }

    /**
     * 运行文件
     *
     * @param fileToRun 待运行文件的路径列表
     */
    void runFile(String fileToRun) throws IOException {
        int exitCode = -1;

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
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        out.println(line);
                        out.flush();
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
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }).start();

            exitCode = process.waitFor();
            out.println("#进程已退出，代码：" + exitCode);
            out.flush();

        } catch (IOException e) {
            throw new IOException();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            out.println("[ERROR] 执行被中断");
            out.flush();
        }
    }

    public static void main(String[] args) {
        fileRunner fileRunner = new fileRunner();
        fileRunner.fileToRun = fileRunner.receiveData();
        try {
            fileRunner.runFile(fileRunner.fileToRun);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
