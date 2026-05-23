"""
Description:

Interactive educational budgeting app using Tkinter for GUI
Pandas for financial data handing
Matplotlib for visualization of data

The budget app is meant for:
1- Tracking  budgeted vs actual spending
2- Learning budgeting basics through the app by trying not to allow “actual” to surpass “budgeted”
3- Creating and monitoring financial goals through visualizations
"""

#import section handles file, gui creation, data processing and visuals
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#constants used throughout the app
DATA_FILE = "budget_data.csv"
GOAL_FILE = "goal_data.csv"
CATEGORIES = ["Food", "Transportation", "Entertainment", "Savings", "Utilities", "Miscellaneous"]

#CSV file if none exists
if not os.path.exists(DATA_FILE):
  initialBudgetData = pd.DataFrame(columns =["category", "budgeted", "actual"])

  initialBudgetData["category"] = CATEGORIES #fills category coloumn with predefined categories
  initialBudgetData["budgeted"] = 0.0 #set to 0
  initialBudgetData["actual"] = 0.0 #set to 0

  #save DataFrame to CSV file
  initialBudgetData.to_csv(DATA_FILE, index= False)

#create goal CSV file if not existent
if not os.path.exists(GOAL_FILE):
  #create empty DataFrame for savings goals
  initialGoalData = pd.DataFrame(columns = ["goalName", "targetAmount", "currentSaved"])
  #save to CSV file
  initialGoalData.to_csv(GOAL_FILE, index=False)

"""
The BudgetApp object creates and manages the educational budgeting app interface

Args:
  root(tk.Tk): Main tkinter app Window

Attributes:
  root (tk.TK): Main app window
  style (ttk.style): GUI styling object
  panedWindow (ttk.PanedWindow)L resizeable container for app panels
  leftFrame (ttk.Frame): Frame containing budgeting controls
  rightFrame (ttk.Frame): Frame containing visuals
  categoryCombo (ttk.Combobox): dropdown for budget categories
  amountEntry (ttk.Entry): user input for budget amounts
  goalNameEntry (ttk.Entry): allow users to input names for their goals
  goalTargetEntry (ttk.Entry): user input for target amounts
  goalCombo (ttk.Combobox): dropdown for savings goals
  goalSaveEntry (ttk.Entry): user input for deposit
  resizeAfterId (str)L store delayed resize callback id

Special Cases:
  AutoResixe layouts
"""

class BudgetApp:
  #object creates and manages app interface
  def __init__(self,root):
    #main frame set up
    self.root = root
    self.root.title("Education Budget")
    screenWidth = self.root.winfo_screenwidth()
    screenHeight = self.root.winfo_screenheight()
    windowWidth = int(screenWidth * 0.85)
    windowHeight = int(screenHeight * 0.85)
    self.root.geometry(f"{windowWidth}x{windowHeight}")
    self.root.minsize(950, 650)
    #allow resizing
    self.root.columnconfigure(0, weight=1)
    self.root.columnconfigure(1, weight=1)
    self.root.rowconfigure(1, weight=1)

    #all GUI sections initiation
    self.createStyles()
    self.createHeader()
    self.panedWindow = ttk.PanedWindow(self.root, orient = tk.HORIZONTAL)
    self.panedWindow.grid(row =1, column=0, sticky="nsew", padx=10, pady=10)
    #left and right panels
    self.leftFrame = ttk.Frame(self.panedWindow, padding=15)
    self.rightFrame = ttk.LabelFrame(self.panedWindow,text = "Financial Charts", padding=10)
    self.panedWindow.add(self.leftFrame, weight=1)
    self.panedWindow.add(self.rightFrame, weight=3)
    #config right frame resizing
    self.rightFrame.columnconfigure(0, weight=1)
    self.rightFrame.rowconfigure(0, weight=1)
    self.createLeftPanel()
    self.refreshVisuals()
    #auto resizing charts
    self.root.bind("<Configure>", self.onResize)

  """
  Create and apply custom GUI styles for labels and themes

  Args:
    None

  Returns:
    None

  Raises:
    None

  Side Effects:
    Modifies ttk styling for app
  """

  def createStyles(self):
    #create ttk style object
    self.style = ttk.Style()
    #create style for subsection labels
    self.style.configure("SubHeader.TLabel", font = ("Arial", 18, "bold"))
    #clam theme for appearance
    self.style.theme_use("clam")
    #style for main title label
    self.style.configure("Header.TLabel", font =("Arial",22, "bold"), foreground="#000080")
    self.style.configure("Edu.TLabel", font =("Arial",16, "italic"), wraplength = 450)

  """
  Creates the top header section of the app

  Args:
    None

  Returns:
    None

  Raises:
    None

  Side Effects:
    Adds labels and frames to GUI
  """

  def createHeader(self):
    #create and display frame for header
    headerFrame = ttk.Frame(self.root, padding = 10)
    headerFrame.grid(row =0, column =0, sticky ="ew", padx =10, pady=10)

    #create and display title for header frame
    titleLabel=ttk.Label(headerFrame, text="Welcome to Your Budget", style = "Header.TLabel")
    titleLabel.grid(row=0, column=0, sticky="w")

    #create and display education description label
    educationLabel = ttk.Label(headerFrame, text="Budgeting helps users control spending, save money, and achieve financial goals.", style="Edu.TLabel")
    educationLabel.grid(row=1, column=0, sticky="w", pady=(5,0))

  """
  Creates the left side panel that contains budgeting and savings goal controls

  Args:
    None

  Returns:
    None

  Raises:
    None

  Side Effects:
    Adds buttons, labels and entry fields to GUI
  """

  def createLeftPanel(self):
    #responsive columns
    for i in range(4):
      self.leftFrame.columnconfigure(i, weight=1)
  
    #budget section
    budgetLabel = ttk.Label(self.leftFrame, text="Category:",font=("Arial", 14, "italic"))
    budgetLabel.grid(row=1, column=0, sticky="w")

    #category dropdown and display
    self.categoryCombo=ttk.Combobox(self.leftFrame, values=CATEGORIES, state="readonly")
    self.categoryCombo.grid(row=1, column=1, padx=5, pady=5,sticky="ew")
    self.categoryCombo.current(0) #set default to 0

    #create and show amount label
    ttk.Label(self.leftFrame, text = "Amount ($):",font=("Arial", 14, "italic")).grid(row=1, column=2, sticky="w")

    #create and display amount entry
    self.amountEntry= ttk.Entry(self.leftFrame)
    self.amountEntry.grid(row=1, column=3, padx=5, sticky="ew")

    #create and display button to set budget value
    setBudgeButton = ttk.Button(self.leftFrame, text="Set Budget", command=lambda: self.updateFinance("budgeted"))
    setBudgeButton.grid(row=2, column=1, pady=5,sticky="ew")

    #create and display log expenses button
    logExpenseButton= ttk.Button(self.leftFrame, text="Log Expenses", command= lambda: self.updateFinance("actual"))
    logExpenseButton.grid(row=2, column=3, pady=5,sticky="ew")

    #educational instruction
    instructionsText = ("Budgeted = Planned spending \nActual = Money already spent \nGoal = Financial target to reach")
    
    #create instruction label and display
    instructionLabel = ttk.Label(self.leftFrame, text = instructionsText, style= "Edu.TLabel")
    instructionLabel.grid(row=3, column =0, sticky="w", pady=(10,15))

    #goal label and display
    goalLabel = ttk.Label(self.leftFrame, text = "Financial Goal Tracking", style ="SubHeader.TLabel",font=("Arial", 14, "bold"))
    goalLabel.grid(row=4, column=0, columnspan=4, sticky="w")

    #goal name label and display
    ttk.Label(self.leftFrame, text="Goal Name:",font=("Arial", 14, "italic")).grid(row=5, column =0, sticky="w")
    
    #create and display goalNameEntry
    self.goalNameEntry = ttk.Entry(self.leftFrame)
    self.goalNameEntry.grid(row=5, column=1, padx=5,sticky="ew")

    #create and display target amount label
    ttk.Label(self.leftFrame, text = "Target ($):",font=("Arial", 14, "italic")).grid(row=5, column=2, sticky = "w")

    #create and display target amount entry box
    self.goalTargetEntry = ttk.Entry(self.leftFrame, width=10)
    self.goalTargetEntry.grid(row=5, column =3, padx=5, sticky="ew")

    #create and display goalButton
    createGoalButton = ttk.Button(self.leftFrame, text = "Create Goal", command= self.addGoal)
    createGoalButton.grid(row=6, column=1, pady=5,sticky="ew")

    #create and display selecting goal label
    ttk.Label(self.leftFrame, text="Select Goal:",font=("Arial", 14, "italic")).grid(row=7, column=0, sticky= "w")
    
    #create and display dropdown menu for goals
    self.goalCombo = ttk.Combobox(self.leftFrame, state = "readonly")
    self.goalCombo.grid(row=7, column=1, padx=5,sticky="ew")

    #create/display deposit amount label
    ttk.Label(self.leftFrame, text= "Deposit \nAmount($):",font=("Arial", 14, "italic")).grid(row=7, column=2, sticky="w")
    
    #create/display deposit entry
    self.goalSaveEntry = ttk.Entry(self.leftFrame)
    self.goalSaveEntry.grid(row=7, column=3, sticky= "ew", padx=5)

    depositButton = ttk.Button(self.leftFrame, text = "Deposit Money", command = self.depositMoneyGoal)
    depositButton.grid(row =8, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

  """
  Update budget or expense data for selected categories

  Args:
    fieldType (str): either budgeted or actual

  Returns:
    None

  Raises:
    ValueError: if amount entered is invalid

  Side Effects:
    Updates CSV data and refreshes visuals
  """

  def updateFinance(self,fieldType):
    #get selected category from dropdown menu
    selectedCategory = self.categoryCombo.get()
    #get amount entered by user
    amountString = self.amountEntry.get()

    #validate user input
    try:
      #convert string to float
      amountValue = float(amountString)

      #error for neg numbers
      if amountValue < 0:
        raise ValueError

    #error for invalid input
    except ValueError:
      messagebox.showerror("Error", "Enter a positive numeric amount")
      return
    
    #load budget data from CSV
    budgetData = pd.read_csv(DATA_FILE)
    #update budgeted amount 
    if fieldType =="budgeted":
      budgetData.loc[budgetData["category"]== selectedCategory, "budgeted"] = amountValue
    #add expense amount to actual spending
    else:
      budgetData.loc[budgetData["category"]== selectedCategory, "actual"] += amountValue
    #save to csv
    budgetData.to_csv(DATA_FILE, index=False)

    #clear amount entry field
    self.amountEntry.delete(0,tk.END)
    #refresh visuals
    self.refreshVisuals()

  """
  Create a new savings goal and store in csv file

  Args:
    None

  Returns:
    None

  Raises:
    ValueError: if target amount is invalid

  Side Effects:
    Updates goal CSV file and refreshVisuals
  """

  def addGoal(self):
    #get goal name
    goalName = self.goalNameEntry.get().strip()
    #get target amount entered by user
    targetString = self.goalTargetEntry.get()

    #validate user input
    try:
      #convert to float
      targetAmount = float(targetString)
      #no 0 or negatives
      if targetAmount <= 0:
        raise ValueError
    #error for invalid target amount
    except ValueError:
      messagebox.showerror("Error", "Enter a valid goal amount")
      return

    #load goalData from CSV file
    goalData = pd.read_csv(GOAL_FILE)

    #prevent duplicates
    if goalName in goalData["goalName"].values:
      messagebox.showerror("Error", "Goal already exists")
      return
    #create DataFrame containing new goal info
    newGoal = pd.DataFrame([{"goalName": goalName, "targetAmount": targetAmount, "currentSaved": 0.0}])
    #add new goal to existing goal data
    goalData = pd.concat([goalData, newGoal], ignore_index =True)

    #save updated file to CSV
    goalData.to_csv(GOAL_FILE, index= False)

    #clear  goal name entry field
    self.goalNameEntry.delete(0,tk.END)
    #clear  target amount entry field
    self.goalTargetEntry.delete(0, tk.END)

    #refresh the visuals
    self.refreshVisuals()

  """
  Deposits monet into existing savings goal

  Args:
    None

  Returns:
    None

  Raises:
    ValueError: deposit amount invalid

  Side Effects:
    Updates goal savings progress and visuals
  """

  def depositMoneyGoal(self):
    #get selected goal from dropdown menu
    selectedGoal= self.goalCombo.get()
    #get deposit amount inputed by user
    depositString = self.goalSaveEntry.get()

    #validate deposit amount
    try:
      #conver to float
      depositAmount = float(depositString)

      #error for 0 or negative
      if depositAmount <= 0:
        raise ValueError
    #error for invalid inputs
    except ValueError:
      messagebox.showerror("Error, enter a positive deposit amount")
      return
    
    #load goal data
    goalData = pd.read_csv(GOAL_FILE)
    #update current saved amount
    goalData.loc[goalData["goalName"]==selectedGoal, "currentSaved"] +=depositAmount
    #save to goal data
    goalData.to_csv(GOAL_FILE, index=False)

    #delete deposit entry field
    self.goalSaveEntry.delete(0, tk.END)

    #update visuals
    self.refreshVisuals()
  
  """
  Refreshes all financial visuals

  Args:
    None

  Returns:
    None

  Raises:
    None

  Side Effects:
    Removes old charts and creates updated charts
  """

  def refreshVisuals(self):
    #remove old charts
    for widget in self.rightFrame.winfo_children():
      widget.destroy()
    
    #load updated data and goal
    budgetData = pd.read_csv(DATA_FILE)
    goalData = pd.read_csv(GOAL_FILE)
    #update goal dropdown menu values
    self.goalCombo["values"] = list(goalData["goalName"].values) 
    #create figure with 2 chart areas and add spacing
    figure, (budgetAxis, goalAxis) = plt.subplots(2,1)
    figure.subplots_adjust(hspace=0.5)
    figure.tight_layout(pad=4.0)

    #budget vs actual bar graph
    categoryIndexes = range(len(budgetData["category"]))
    barWidth = 0.35 #bar width

    #create budgeted and acutal spending bars
    budgetAxis.bar(categoryIndexes, budgetData["budgeted"], width = barWidth, label ="Budgeted", color = "#3498DB")
    budgetAxis.bar([index + barWidth for index in categoryIndexes], budgetData["actual"], width = barWidth, label = "Actual", color = "#E74C3C")
    #title for spending chart
    budgetAxis.set_title("Budget vs Actual Spending")
    #category names location
    budgetAxis.set_xticks([index + barWidth / 2 for index in categoryIndexes])
    budgetAxis.set_xticklabels(budgetData["category"], rotation =15)
    budgetAxis.legend() #chart legend

    #goal progress bar chart when existing
    if len(goalData) > 0:
      #turns to percentage
      goalPercentages = (goalData["currentSaved"] / goalData["targetAmount"]) * 100
      #percentage can't exceed 100
      goalPercentages = goalPercentages.clip(upper =100)
      #horizontal bar for goals
      goalAxis.barh(goalData["goalName"], goalPercentages, color = "#2ECC71")
      goalAxis.set_xlim(0,100)
      goalAxis.set_title("Savings Goal Progress")
      goalAxis.set_xlabel("Completion Percentage")
    #message when no goals
    else:
      goalAxis.text(0.5, 0.5, "No goals created", ha ="center")
    
    #display in tkinter window
    chartCanvas = FigureCanvasTkAgg(figure, master = self.rightFrame)
    chartCanvas.draw()
    canvasWidget =chartCanvas.get_tk_widget()
    canvasWidget.grid(row=0, column=0, sticky="nsew")

  """
  Handles window resizing events and refreshes the visuals dynamically

  Args:
    event (tk.Event): resize event triggered by tkinter

  Returns:
    None

  Raises:
    None

  Side Effects:
    Refreshes financial visuals when window size changes
  """

  def onResize(self,event):
    #prevents excessive redraw lag
    if event.widget == self.root:
      self.refreshVisuals()

#main program
if __name__ =="__main__":
  #create main tkinter app window
  rootWindow = tk.Tk()
  #create BudgetApp object
  budgetApp = BudgetApp(rootWindow)
  #run app event loop
  rootWindow.mainloop()
