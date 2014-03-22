import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;

class PQMFG_TCP_Client
{
	private Socket clientSocket = null;

	PQMFG_TCP_Client(String IpAddress, int PortNum) throws UnknownHostException, IOException
	{
		clientSocket = new Socket(IpAddress, PortNum);
	}

	public String[] sendCommand(String command) throws IOException
	{
		String[] returnString = null;
		ArrayList<String> MessageList = new ArrayList<String>();


		DataOutputStream outToServer  = new DataOutputStream(clientSocket.getOutputStream());
		BufferedReader inFromServer = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));

		outToServer.writeBytes(command);
		String sentence =null;

		while((sentence= inFromServer.readLine())!="#END")
		{
			MessageList.add(sentence);
		}

		if(!MessageList.isEmpty())
		{
			returnString = new String[MessageList.size()];

			int count = 0;
			while(!MessageList.isEmpty())
			{
				returnString[count] = MessageList.remove(0);
				count++;
			}
			
		}

		return returnString;
	}
	public void closeSocket() throws IOException
	{
		clientSocket.close();
	}
}