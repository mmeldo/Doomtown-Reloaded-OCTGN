#winForms.py

try:
   import clr
   clr.AddReference("System.Drawing")
   clr.AddReference("System.Windows.Forms")

   from System.Windows.Forms import *
   from System.Drawing import Color
except:
   Automations['WinForms'] = False

#---------------------------------------------------------------------------
# Custom Windows Forms
#---------------------------------------------------------------------------

class OKWindow(Form): # This is a WinForm which creates a simple window, with some text and an OK button to close it.
   def __init__(self,InfoTXT):
      self.StartPosition = FormStartPosition.CenterScreen
      (STRwidth, STRheight) = calcStringLabelSize(InfoTXT)
      FORMheight = 160 + STRheight
      FORMwidth = 100 + STRwidth
      self.Text = 'Information'
      self.Height = FORMheight
      self.Width = FORMwidth
      self.AutoSize = True
      self.MinimizeBox = False
      self.MaximizeBox = False
      self.TopMost = True
      
      labelPanel = Panel()
      labelPanel.Dock = DockStyle.Top
      labelPanel.AutoSize = True
      labelPanel.BackColor = Color.White

      self.timer_tries = 0
      self.timer = Timer()
      self.timer.Interval = 200
      self.timer.Tick += self.onTick
      self.timer.Start()
      
      label = Label()
      label.Text = formStringEscape(InfoTXT)
      if debugVerbosity >= 2: label.Text += '\n\nTopMost: ' + str(self.TopMost) # Debug
      label.Top = 30
      label.Left = (self.ClientSize.Width - STRwidth) / 2
      label.Height = STRheight
      label.Width = STRwidth
      labelPanel.Controls.Add(label)
      #label.AutoSize = True #Well, that's shit.

      button = Button()
      button.Text = "OK"
      button.Width = 100
      button.Top = FORMheight - 80
      button.Left = (FORMwidth - 100) / 2
      button.Anchor = AnchorStyles.Bottom

      button.Click += self.buttonPressed

      self.Controls.Add(labelPanel)
      self.Controls.Add(button)

   def buttonPressed(self, sender, args):
      self.timer.Stop()
      self.Close()

   def onTick(self, sender, event):
      if self.timer_tries < 3:
         self.TopMost = False
         self.Focus()
         self.Activate()
         self.TopMost = True
         self.timer_tries += 1

class SingleChoiceWindow(Form):
 
   def __init__(self, BoxTitle, BoxOptions, type, defaultOption, pages = 0, cancelButtonBool = True, cancelName = 'Cancel'):
      self.Text = "Select an Option"
      self.index = 0
      self.confirmValue = None
      self.MinimizeBox = False
      self.MaximizeBox = False
      self.StartPosition = FormStartPosition.CenterScreen
      self.AutoSize = True
      self.TopMost = True
      
      (STRwidth, STRheight) = calcStringLabelSize(BoxTitle)
      self.Width = STRwidth + 50

      self.timer_tries = 0
      self.timer = Timer()
      self.timer.Interval = 200
      self.timer.Tick += self.onTick
      self.timer.Start()
      
      labelPanel = Panel()
      labelPanel.Dock = DockStyle.Top
      labelPanel.AutoSize = True
      labelPanel.BackColor = Color.White
      
      separatorPanel = Panel()
      separatorPanel.Dock = DockStyle.Top
      separatorPanel.Height = 20
      
      choicePanel = Panel()
      choicePanel.Dock = DockStyle.Top
      choicePanel.AutoSize = True

      self.Controls.Add(labelPanel)
      labelPanel.BringToFront()
      self.Controls.Add(separatorPanel)
      separatorPanel.BringToFront()
      self.Controls.Add(choicePanel)
      choicePanel.BringToFront()

      label = Label()
      label.Text = formStringEscape(BoxTitle)
      if debugVerbosity >= 2: label.Text += '\n\nTopMost: ' + str(self.TopMost) # Debug
      label.Top = 30
      label.Left = (self.ClientSize.Width - STRwidth) / 2
      label.Height = STRheight
      label.Width = STRwidth
      labelPanel.Controls.Add(label)
      
      bufferPanel = Panel() # Just to put the radio buttons a bit more to the middle
      bufferPanel.Left = (self.ClientSize.Width - bufferPanel.Width) / 2
      bufferPanel.AutoSize = True
      choicePanel.Controls.Add(bufferPanel)
            
      for option in BoxOptions:
         if type == 'radio':
            btn = RadioButton()
            if defaultOption == self.index: btn.Checked = True
            else: btn.Checked = False
            btn.CheckedChanged += self.checkedChanged
         else: 
            btn = Button()
            btn.Height = calcStringButtonHeight(formStringEscape(option))
            btn.Click += self.choiceMade
         btn.Name = str(self.index)
         self.index = self.index + 1
         btn.Text = formStringEscape(option)
         btn.Dock = DockStyle.Top
         bufferPanel.Controls.Add(btn)
         btn.BringToFront()

      button = Button()
      button.Text = "Confirm"
      button.Width = 100
      button.Dock = DockStyle.Bottom
      button.Click += self.buttonPressed
      if type == 'radio': self.Controls.Add(button) # We only add the "Confirm" button on a radio menu.
 
      buttonNext = Button()
      buttonNext.Text = "Next Page"
      buttonNext.Width = 100
      buttonNext.Dock = DockStyle.Bottom
      buttonNext.Click += self.nextPage
      if pages > 1: self.Controls.Add(buttonNext) # We only add the "Confirm" button on a radio menu.

      cancelButton = Button() # We add a bytton to Cancel the selection
      cancelButton.Text = cancelName # We can rename the cancel button if we want to.
      cancelButton.Width = 100
      cancelButton.Dock = DockStyle.Bottom
      #button.Anchor = AnchorStyles.Bottom
      cancelButton.Click += self.cancelPressed
      if cancelButtonBool: self.Controls.Add(cancelButton)
      
   def buttonPressed(self, sender, args):
      self.timer.Stop()
      self.Close()

   def nextPage(self, sender, args):
      self.confirmValue = "Next Page"
      self.timer.Stop()
      self.Close()
 
   def cancelPressed(self, sender, args): # The function called from the cancelButton
      self.confirmValue = None # It replaces the choice list with an ABORT message which is parsed by the calling function
      self.timer.Stop()
      self.Close() # And then closes the form
      
   def checkedChanged(self, sender, args):
      self.confirmValue = sender.Name
      
   def choiceMade(self, sender, args):
      self.confirmValue = sender.Name
      self.timer.Stop()
      self.Close()
      
   def getIndex(self):
      return self.confirmValue

   def onTick(self, sender, event):
      if self.timer_tries < 3:
         self.TopMost = False
         self.Focus()
         self.Activate()
         self.TopMost = True
         self.timer_tries += 1

class MultiChoiceWindow(Form):
 # This is a windows form which creates a multiple choice form, with a button for each choice. 
 # The player can select more than one, and they are then returned as a list of integers
   def __init__(self, FormTitle, FormChoices,CPType, pages = 0,currPage = 0, existingChoices = []): # We initialize our form, expecting 3 variables. 
                                                      # FormTitle is the title of the window itself
                                                      # FormChoices is a list of strings which we use for the names of the buttons
                                                      # CPType is combined with FormTitle to give a more thematic window name.
      self.Text = CPType # We just store the variable locally
      self.index = 0 # We use this variable to set a number to each button
      self.MinimizeBox = False # We hide the minimize button
      self.MaximizeBox = False # We hide the maximize button
      self.StartPosition = FormStartPosition.CenterScreen # We start the form at the center of the player's screen
      self.AutoSize = True # We allow the form to expand in size depending on its contents
      self.TopMost = True # We make sure our new form will be on the top of all other windows. If we didn't have this here, fullscreen OCTGN would hide the form.
      self.origTitle = formStringEscape(FormTitle) # Used when modifying the label from a button
      
      self.confirmValue = existingChoices
      debugNotify("existingChoices = {}".format(self.confirmValue))
      self.nextPageBool = False  # self.nextPageBool is just remembering if the player has just flipped the page.
      self.currPage = currPage
      
      self.timer_tries = 0 # Ugly hack to fix the form sometimes not staying on top of OCTGN
      self.timer = Timer() # Create a timer object
      self.timer.Interval = 200 # Speed is at one 'tick' per 0.2s
      self.timer.Tick += self.onTick # Activate the event function on each tick
      self.timer.Start() # Start the timer.
      
      (STRwidth, STRheight) = calcStringLabelSize(FormTitle) # We dynamically calculate the size of the text label to be displayed as info to the player.
      labelPanel = Panel() # We create a new panel (e.g. container) to store the label.
      labelPanel.Dock = DockStyle.Top # We Dock the label's container on the top of the form window
      labelPanel.Height = STRheight # We setup the dynamic size
      labelPanel.Width = STRwidth
      labelPanel.AutoSize = True # We allow the panel to expand dynamically according to the size of the label
      labelPanel.BackColor = Color.White
      
      choicePanel = Panel() # We create a panel to hold our buttons
      choicePanel.Dock = DockStyle.Top # We dock this below the label panel
      choicePanel.AutoSize = True # We allow it to expand in size dynamically
      #radioPanel.BackColor = Color.LightSalmon # Debug

      separatorPanel = Panel() # We create a panel to separate the labels from the buttons
      separatorPanel.Dock = DockStyle.Top # It's going to be docked to the middle of both
      separatorPanel.Height = 20 # Only 20 pixels high

      self.Controls.Add(labelPanel) # The panels need to be put in the form one by one
      labelPanel.BringToFront() # This basically tells that the last panel we added should go below all the others that are already there.
      self.Controls.Add(separatorPanel)
      separatorPanel.BringToFront() 
      self.Controls.Add(choicePanel) 
      choicePanel.BringToFront() 

      self.label = Label() # We create a label object which will hold the multiple choice description text
      #if len(self.confirmValue): self.label.Text = formStringEscape(FormTitle) + "\n\nYour current choices are:\n{}".format(self.confirmValue) # We display what choices we've made until now to the player.
      self.label.Text = formStringEscape(FormTitle) # We escape any strings that WinForms doesn't like, like ampersand and store it in the label
      if debugVerbosity >= 2: self.label.Text += '\n\nTopMost: ' + str(self.TopMost) # Debug
      self.label.Top = 30 # We place the label 30 pixels from the top size of its container panel, and 50 pixels from the left.
      self.label.Left = 50
      self.label.Height = STRheight # We set its dynamic size
      self.label.Width = STRwidth
      labelPanel.Controls.Add(self.label) # We add the label to its container
      
      choicePush = Panel() # An extra secondary container for the buttons, that is not docked, to allow us to slightly change its positioning
      choicePush.Left = (self.ClientSize.Width - choicePush.Width) / 2 # We move it 50 pixels to the left
      choicePush.AutoSize = True # We allow it to expand dynamically
      choicePanel.Controls.Add(choicePush) # We add it to its parent container
      
      for option in FormChoices: # We dynamically add as many buttons as we have options
         btn = Button() # We initialize a button object
         btn.Name = str(self.index) # We name the button equal to its numeric value, plus its effect.
         btn.Text = str(self.index) + ':--> ' + formStringEscape(option)
         self.index = self.index + 1 # The internal of the button is also the choice that will be put in our list of integers. 
         btn.Dock = DockStyle.Top # We dock the buttons one below the other, to the top of their container (choicePush)
         btn.AutoSize = True # Doesn't seem to do anything
         btn.Height = calcStringButtonHeight(formStringEscape(option))
         btn.Click += self.choiceMade # This triggers the function which records each choice into the confirmValue[] list
         choicePush.Controls.Add(btn) # We add each button to its panel
         btn.BringToFront() # Add new buttons to the bottom of existing ones (Otherwise the buttons would be placed in reverse numerical order)

      buttonNext = Button()
      buttonNext.Text = "Next Page"
      buttonNext.Width = 100
      buttonNext.Dock = DockStyle.Bottom
      buttonNext.Click += self.nextPage
      if pages > 1: self.Controls.Add(buttonNext) # We only add the "Confirm" button on a radio menu.

      finishButton = Button() # We add a button to Finish the selection
      finishButton.Text = "Finish Selection"
      finishButton.Width = 100
      finishButton.Dock = DockStyle.Bottom # We dock it to the bottom of the form.
      #button.Anchor = AnchorStyles.Bottom
      finishButton.Click += self.finishPressed # We call its function
      self.Controls.Add(finishButton) # We add the button to the form
 
      cancelButton = Button() # We add a bytton to Cancel the selection
      cancelButton.Text = "Cancel"
      cancelButton.Width = 100
      cancelButton.Dock = DockStyle.Bottom
      #button.Anchor = AnchorStyles.Bottom
      cancelButton.Click += self.cancelPressed
      self.Controls.Add(cancelButton)

   def nextPage(self, sender, args):
      self.nextPageBool = True
      self.timer.Stop()
      self.Close()
 
   def finishPressed(self, sender, args): # The function called from the finishButton.
      self.timer.Stop()
      self.Close()  # It just closes the form

   def cancelPressed(self, sender, args): # The function called from the cancelButton
      self.confirmValue = 'ABORT' # It replaces the choice list with an ABORT message which is parsed by the calling function
      self.timer.Stop()
      self.Close() # And then closes the form
 
   def choiceMade(self, sender, args): # The function called when pressing one of the choice buttons
      self.confirmValue.append((self.currPage * 7) + int(sender.Name)) # We append the button's name to the existing choices list
      self.label.Text = self.origTitle + "\n\nYour current choices are:\n{}".format(self.confirmValue) # We display what choices we've made until now to the player.
 
   def getIndex(self): # The function called after the form is closed, to grab its choices list
      if self.nextPageBool: 
         self.nextPageBool = False
         return "Next Page"
      else: return self.confirmValue

   def getStoredChoices(self): # The function called after the form is closed, to grab its choices list
      return self.confirmValue

   def onTick(self, sender, event): # Ugly hack required because sometimes the winform does not go on top of all
      if self.timer_tries < 3: # Try three times to bring the form on top
         if debugVerbosity >= 2: self.label.Text = self.origTitle + '\n\n### Timer Iter: ' + str(self.timer_tries)
         self.TopMost = False # Set the form as not on top
         self.Focus() # Focus it
         self.Activate() # Activate it
         self.TopMost = True # And re-send it to top
         self.timer_tries += 1 # Increment this counter to stop after 3 tries.