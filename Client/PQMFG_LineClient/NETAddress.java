import java.net.InetAddress;
import java.net.UnknownHostException;

public class NETAddress 
{
    int Port;
    InetAddress IP;
    // etc
    
    public NETAddress()
    {
        int Port = -1;
        String IP = null;
    }
    
    public boolean setIP(String input)
    {
    	boolean myReturn = false;
    	
    	try 
    	{
    		IP = InetAddress.getByName(input);
    		myReturn = true;
    	} 
    	catch (UnknownHostException e) 
    	{
			IP = null;
		}
    	
    	return myReturn;
    }
    
    public boolean setport(int input)
    {
    	boolean myRetrun = false;
    	
    	if (input > 0 )
    	{
    		myRetrun = true;
    		Port = input;
    	}
    	
    	return myRetrun;
    }
    public boolean setport(String input)
    {
    	
    	boolean myRetrun = false;   	
    	int x = Integer.parseInt(input);
    	
    	if (x > 0)
    	{
    		myRetrun = true;
    		Port = x;
    	}
    	
    	return myRetrun;
    }
    
    
}