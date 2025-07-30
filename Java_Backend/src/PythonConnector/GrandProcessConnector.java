package PythonConnector;

/**
 * 与Python主进程通信的连接器接口
 *
 * @param <Tr> 接收的数据类型
 * @param <Ts> 返回给主进程的数据类型
 */
public interface GrandProcessConnector<Tr, Ts> {

    /**
     * 从标准输入接收参数
     *
     * @return 接收到的参数
     */
    Tr receiveData();

    /**
     * 向标准输出发送参数
     *
     * @param data 需要发送的数据
     */
    void sendData(Ts data);
}
