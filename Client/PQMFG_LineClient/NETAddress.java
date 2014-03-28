import java.net.InetAddress;
import java.net.UnknownHostException;
/**
 * MADE THIS for some Variable holding
 * */
public class NETAddress 
{
	//2 variables... a Port# and a IP address
    int Port;
    InetAddress IP;
    
    //Simple constructer
    public NETAddress()
    {
        int Port = -1;
        String IP = null;
    }
    
    /*
     * Getters and Setters
     * */
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
    /*
     * Getters and Setters
     * */
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
    /*
     * Getters and Setters
     * */
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