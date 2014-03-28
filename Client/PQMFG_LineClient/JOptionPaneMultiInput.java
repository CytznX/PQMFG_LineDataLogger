import javax.swing.*;

public class JOptionPaneMultiInput 
{
	private static JTextField IP = new JTextField(10);
	private static JTextField Port = new JTextField(5);
	private static JPanel myPanel = new JPanel();

	public JOptionPaneMultiInput()
	{
		IP.setText("127.0.0.1");
		Port.setText("5006");
		
		myPanel.add(new JLabel("IP:"));
		myPanel.add(IP);
		myPanel.add(Box.createHorizontalStrut(10)); // a spacer
		myPanel.add(new JLabel("Port:"));
		myPanel.add(Port);
	}
	public NETAddress ask() 
	{
		NETAddress myAdress = new NETAddress();

		int result = JOptionPane.showConfirmDialog(null, myPanel, 
				"Enter Server IP and Port Values", 
				JOptionPane.OK_CANCEL_OPTION);
		
		
		if (result == JOptionPane.OK_OPTION) {
			
			myAdress.setIP(IP.getText());
			myAdress.setport(Port.getText());
		}

		return myAdress;
	}
}