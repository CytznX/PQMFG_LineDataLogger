import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.Socket;
import java.util.ArrayList;

import javax.jws.soap.SOAPBinding.Use;

public class ClientAlpha
{
	//Some Initial Class Variables
	private Socket ServerSocket = null;
	private InetAddress ServerIpAddress = null;
	private int ServerPortNum = 5006;
	
	//The Main METHOD!!! OMG!!!
	public static void main(String[] args) 
	{
		new ClientAlpha(0,0);
	}
	
	//Default Constructor
	public ClientAlpha(int width,int Height)
	{
		
		/**
		 * Ask User To point At Server
		 * */
		
		//Create a Multi-line input box
		JOptionPaneMultiInput UserPrompt = new JOptionPaneMultiInput();
		NETAddress myAdress = UserPrompt.ask();// *NOTE: NET Adrees simple class i pout together for passing back and forth net addresses
		
		//Asighned returned shit to class variabls
		ServerIpAddress = myAdress.IP;
		ServerPortNum = myAdress.Port;
		
		/**
		 * Heres where we try and open up a connection to the server
		 * */
		try 
		{
			ServerSocket = new Socket(ServerIpAddress, ServerPortNum);
			System.out.println("got it");
		} 
		catch (IOException e) {
			System.out.println("Could Not Open connection to Server At: "+ServerIpAddress+" "+Integer.toString(ServerPortNum));
		}
		

		
		
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
	
}