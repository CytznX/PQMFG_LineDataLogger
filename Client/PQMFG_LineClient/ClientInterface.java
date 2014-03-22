import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.text.DecimalFormat;

import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.DefaultComboBoxModel;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.SpringLayout;

public class ClientInterface
{

	//Preloaded values for Address File and Machine count <I was getting Lazy>
	private static  final String Addressfile = "MachineAddress.txt";
	private static final int numOfMachines = 14;
	
	//Udp Com stuff
	private static PQMFG_TCP_Client TCPcom;
	private static boolean Connected = false;
	private static String[][] MachineUDPinfo;

	//some odds and ends... =P ... GAP is for GUI esthetics, and df is for formating outputs
	private final static int GAP = 10;
	private DecimalFormat df = new DecimalFormat("#.##");
	
	//Output Jtext Area and input JtextFields
	private JTextArea MachineInfo, LineLeaders, Mechanics, LineWorkers;
	private JTextField IPField, PortField, UDPSend;
	private JComboBox comboBox;
	
	//Main Method envokes default constructer
	public static void main(String[] args) 
	{
		new ClientInterface(860,720);
	}

	//Default Constructor
	public ClientInterface(int windowWidth, int windowHeight)
	{
		//Creates the panel holder(JFrame)
		JFrame guiFrame = new JFrame();

		//Creates Imports UDP Info from "Addressfile"
		MachineUDPinfo = getMachineAdress(numOfMachines);

		//make sure the program exits when the frame closes
		guiFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		guiFrame.setTitle("UDP Debug GUI");
		guiFrame.setSize(windowWidth,windowHeight);

		//The JFrame uses the BorderLayout layout manager.
		//Put the two JPanels and JButton in different areas.
		guiFrame.add(createEntryFields(), BorderLayout.NORTH);
		guiFrame.add(createTextFields(), BorderLayout.CENTER);
		guiFrame.add(createButtons(),BorderLayout.WEST);


		//This will center the JFrame in the middle of the screen
		guiFrame.setLocationRelativeTo(null);

		//make sure the JFrame is visible
		guiFrame.setVisible(true);
	}

	/*
	 * Creates the button panel on left side of GUI
	 * Also contains actionListener methods for all buttons
	 * */
	protected JComponent createButtons() {

		//Creates pannel that will be returned to constructor for later use
		JPanel panel = new JPanel(new GridLayout(0,1, 10 ,10));

		//Creates the two Jbuttons that will be epic!!!
		JButton AddEmpButton = new JButton( "Add Employee");
		JButton RemoveEmpButton = new JButton( "Remove Employee");
		JButton MachineUpButton = new JButton( "Machine Up");
		JButton MachineDownButton = new JButton( "Machine Down");

		JButton ConectButton = new JButton( "Connect");
		JButton RefeshButton = new JButton( "Refresh");
		JButton LogoutButton = new JButton( "Logout");
		
        DefaultComboBoxModel model = new DefaultComboBoxModel();
        model.addElement("<Select a Machine>");
        
        for (int i = 0; i < MachineUDPinfo.length; i++) 
        {
        	model.addElement(MachineUDPinfo[i][0]);
		}
        comboBox = new JComboBox(model);
        
		
        //To get input from combo box
        //comboBox.getSelectedItem()
		

		//The ActionListener class is used to handle the
		//event that happens when the user clicks the button.
		//As there is not a lot that needs to happen we can 
		//define an anonymous inner class to make the code simpler.
        ConectButton.addActionListener(new ActionListener()
		{
			@Override
			public void actionPerformed(ActionEvent event)
			{
				
				//converts IP address and Port to proper forms
				int port = -1;
				String IPAddress = null;
				
			    for(int i =0; i < MachineUDPinfo.length; i++)
			    {
			    	System.out.println(MachineUDPinfo[i][0]);
			    	System.out.println(comboBox.getSelectedItem());
			    	
			        if(MachineUDPinfo[i][0].contains((CharSequence) comboBox.getSelectedItem()))
			        {
			        	IPAddress = MachineUDPinfo[i][1];
						port = Integer.parseInt(MachineUDPinfo[i][2]);
			        	
			        }
			    }
				
				//Checks to see if input textfields are populated with valid data
				if(port!=(-1) && IPAddress!=null)
				{	
					try 
					{
						TCPcom = new PQMFG_TCP_Client(IPAddress, port);
					} 
					catch (UnknownHostException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					} 
					catch (IOException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				}
			}
		});

		//add everything to pannel and the pass it back...
		panel.add(comboBox);
		panel.add(ConectButton);
		panel.add(RefeshButton);
		panel.add(LogoutButton); 
		panel.add(new JLabel("===============================")); 
		panel.add(AddEmpButton);
		panel.add(RemoveEmpButton);
		panel.add(MachineUpButton);
		panel.add(MachineDownButton);

		return panel; 
	}
	
	/*
	 * Creates Output Field for Right half of GUI
	 * */
	protected JComponent createTextFields() 
	{
		
		//LineLeaders, Mechanics, LineWorkers
		
		//creates & formats panel that will be passed back later 
		JPanel panel = new JPanel();
		panel.setLayout(new BoxLayout(panel, BoxLayout.PAGE_AXIS));
		
		//Creates and formats non-mutable text area for Return messages
		LineLeaders = new JTextArea("-----NO DATA AVALIBLE-----\n");
		LineLeaders.setFont(new Font("Serif", Font.PLAIN, 12));
		LineLeaders.setEditable(false);
		//LineLeaders.setLineWrap(true);
		LineLeaders.setWrapStyleWord(true);
		panel.add(createNewSP(LineLeaders, "Current Line Leaders", 250,250));
		
		//Creates and formats non-mutable text area for Return messages
		Mechanics = new JTextArea("-----NO DATA AVALIBLE-----\n");
		Mechanics.setFont(new Font("Serif", Font.PLAIN, 12));
		Mechanics.setEditable(false);
		//Mechanics.setLineWrap(true);
		Mechanics.setWrapStyleWord(true);
		panel.add(createNewSP(Mechanics, "Current Mechanics", 250,250));
		
		//Creates and formats non-mutable text area for Return messages
		LineWorkers = new JTextArea("-----NO DATA AVALIBLE-----\n");
		LineWorkers.setFont(new Font("Serif", Font.PLAIN, 12));
		LineWorkers.setEditable(false);
		//LineWorkers.setLineWrap(true);
		LineWorkers.setWrapStyleWord(true);
		panel.add(createNewSP(LineWorkers, "Current Line Workers", 250,250));
		
		return panel;
	}
	
	/*
	 * Creates output banner at top of GUI
	 * */
	private JComponent createEntryFields() 
	{
		//creates & formats panel that will be passed back later 
		JPanel panel = new JPanel();
		panel.setLayout(new BoxLayout(panel, BoxLayout.PAGE_AXIS));

		//creates the lables for input fields
		//creates the lables for input fields
		//Creates and formats non-mutable text area for Return messages
		MachineInfo = new JTextArea("-----NOT CONECTED-----\n");
		MachineInfo.setFont(new Font("Serif", Font.PLAIN, 12));
		MachineInfo.setEditable(false);
		//LineLeaders.setLineWrap(true);
		MachineInfo.setWrapStyleWord(true);
		panel.add(createNewSP(MachineInfo, "Machine Status", 250,250));
		
		//returns the pannel
		return panel;
	}
	
	/*
	 * Reads in Machine addresses from txt file and creates array of 
	 * */
	public static String[][] getMachineAdress(int NumOfMachines)
	{
		String[][] returnArray = new String[NumOfMachines][3];

		//Attempts to open new buffered reader
		try 
		{
			//Reads the specified file from AddressFile
			BufferedReader br = new BufferedReader(new FileReader(Addressfile));
			try
			{
				///Initialize some placeHolderVariables
				String line = "";
				int count = 0;

				//Loops through all the lines fo are file
				while ((line = br.readLine()) != null && (count)<NumOfMachines) 
				{
					//Splits the string by whitespace (<SPACE>,<TAB>, etc)
					String[] Split = line.split("\\s+");
					//If the result is the correct length accept as valid, else ignore
					if(Split.length == 3)
					{
						//write corresponding info to positions
						returnArray[count][0]=Split[0];
						returnArray[count][1]=Split[1];
						returnArray[count][2]=Split[2];
					}
					else
					{
						//flag error
						System.out.println("Error at line: #" +(count+1));
					}
					//Increment count
					count++;
				}
				//close reader when done
				br.close();
			}
			//catch one of the most epic errors of all time ... the dreaded IOException
			catch(IOException e)
			{
				System.out.println(e);
			}

		} 
		//if the file doesnt exist tell me
		catch (FileNotFoundException e1) 
		{
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}

		//return the populated array
		return returnArray;
	}

	/*
	 * Creates fancy boarders for JTextAreas 
	 * */
	private JScrollPane createNewSP(JTextArea passedTextArea,String Header, int DimX, int DimY)
	{
		//creates & Formats object that holds and navigates text area
        JScrollPane areaScrollPane = new JScrollPane(passedTextArea);
        areaScrollPane.setVerticalScrollBarPolicy(
                        JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
        areaScrollPane.setPreferredSize(new Dimension(DimX, DimY));
        
        //More Formatting
        areaScrollPane.setBorder(
            BorderFactory.createCompoundBorder(
                BorderFactory.createCompoundBorder(
                                BorderFactory.createTitledBorder(Header),
                                BorderFactory.createEmptyBorder(5,5,5,5)),
                areaScrollPane.getBorder()));

		
		return areaScrollPane;
	}
}