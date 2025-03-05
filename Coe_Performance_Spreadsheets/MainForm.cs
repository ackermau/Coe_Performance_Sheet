using System;
using System.Windows.Forms;

namespace RFQForm
{
    public partial class MainForm : Form
    {
        public MainForm()
        {
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            this.Text = "Request for Quote";
            this.Size = new System.Drawing.Size(800, 600);

            // Add a button to open the Table of Contents
            Button tocButton = new Button() { Text = "Table of Contents", Location = new System.Drawing.Point(10, 460) };
            tocButton.Click += (sender, e) => OpenTableOfContents();

            // Add a button to open the Material Specifications
            Button materialSpecsButton = new Button() { Text = "Material Specifications", Location = new System.Drawing.Point(150, 460) };
            materialSpecsButton.Click += (sender, e) => OpenMaterialSpecifications();

            // Add controls to the form
            this.Controls.Add(tocButton);
            this.Controls.Add(materialSpecsButton);

            // Customer Information
            Label customerLabel = new Label() { Text = "Customer:", Location = new System.Drawing.Point(10, 10) };
            TextBox customerTextBox = new TextBox() { Location = new System.Drawing.Point(150, 10) };

            Label dateLabel = new Label() { Text = "Date:", Location = new System.Drawing.Point(10, 40) };
            TextBox dateTextBox = new TextBox() { Location = new System.Drawing.Point(150, 40) };

            Label referenceLabel = new Label() { Text = "Reference:", Location = new System.Drawing.Point(10, 70) };
            TextBox referenceTextBox = new TextBox() { Location = new System.Drawing.Point(150, 70) };

            // Coil Specifications
            Label coilWidthLabel = new Label() { Text = "Coil Width (in):", Location = new System.Drawing.Point(10, 100) };
            TextBox coilWidthTextBox = new TextBox() { Location = new System.Drawing.Point(150, 100) };

            Label coilWeightLabel = new Label() { Text = "Coil Weight:", Location = new System.Drawing.Point(10, 130) };
            TextBox coilWeightTextBox = new TextBox() { Location = new System.Drawing.Point(150, 130) };

            Label materialThicknessLabel = new Label() { Text = "Material Thickness (in):", Location = new System.Drawing.Point(10, 160) };
            TextBox materialThicknessTextBox = new TextBox() { Location = new System.Drawing.Point(150, 160) };

            Label materialTypeLabel = new Label() { Text = "Material Type:", Location = new System.Drawing.Point(10, 190) };
            TextBox materialTypeTextBox = new TextBox() { Location = new System.Drawing.Point(150, 190) };

            Label yieldStrengthLabel = new Label() { Text = "Yield Strength (psi):", Location = new System.Drawing.Point(10, 220) };
            TextBox yieldStrengthTextBox = new TextBox() { Location = new System.Drawing.Point(150, 220) };

            Label materialTensileLabel = new Label() { Text = "Material Tensile (psi):", Location = new System.Drawing.Point(10, 250) };
            TextBox materialTensileTextBox = new TextBox() { Location = new System.Drawing.Point(150, 250) };

            Label requiredMaxFPMLabel = new Label() { Text = "Required Maximum FPM:", Location = new System.Drawing.Point(10, 280) };
            TextBox requiredMaxFPMTextBox = new TextBox() { Location = new System.Drawing.Point(150, 280) };

            Label minBendRadiusLabel = new Label() { Text = "Minimum Bend Radius (in):", Location = new System.Drawing.Point(10, 310) };
            TextBox minBendRadiusTextBox = new TextBox() { Location = new System.Drawing.Point(150, 310) };

            Label minLoopLengthLabel = new Label() { Text = "Min Loop Length (ft):", Location = new System.Drawing.Point(10, 340) };
            TextBox minLoopLengthTextBox = new TextBox() { Location = new System.Drawing.Point(150, 340) };

            Label coilODLabel = new Label() { Text = "Coil O.D.:", Location = new System.Drawing.Point(10, 370) };
            TextBox coilODTextBox = new TextBox() { Location = new System.Drawing.Point(150, 370) };

            Label coilIDLabel = new Label() { Text = "Coil I.D.:", Location = new System.Drawing.Point(10, 400) };
            TextBox coilIDTextBox = new TextBox() { Location = new System.Drawing.Point(150, 400) };

            // Add a button to process the information
            Button processButton = new Button() { Text = "Process", Location = new System.Drawing.Point(10, 430) };
            processButton.Click += (sender, e) => ProcessInformation(
                customerTextBox.Text,
                dateTextBox.Text,
                referenceTextBox.Text,
                coilWidthTextBox.Text,
                coilWeightTextBox.Text,
                materialThicknessTextBox.Text,
                materialTypeTextBox.Text,
                yieldStrengthTextBox.Text,
                materialTensileTextBox.Text,
                requiredMaxFPMTextBox.Text,
                minBendRadiusTextBox.Text,
                minLoopLengthTextBox.Text,
                coilODTextBox.Text,
                coilIDTextBox.Text
            );

            // Add controls to the form
            this.Controls.Add(customerLabel);
            this.Controls.Add(customerTextBox);
            this.Controls.Add(dateLabel);
            this.Controls.Add(dateTextBox);
            this.Controls.Add(referenceLabel);
            this.Controls.Add(referenceTextBox);
            this.Controls.Add(coilWidthLabel);
            this.Controls.Add(coilWidthTextBox);
            this.Controls.Add(coilWeightLabel);
            this.Controls.Add(coilWeightTextBox);
            this.Controls.Add(materialThicknessLabel);
            this.Controls.Add(materialThicknessTextBox);
            this.Controls.Add(materialTypeLabel);
            this.Controls.Add(materialTypeTextBox);
            this.Controls.Add(yieldStrengthLabel);
            this.Controls.Add(yieldStrengthTextBox);
            this.Controls.Add(materialTensileLabel);
            this.Controls.Add(materialTensileTextBox);
            this.Controls.Add(requiredMaxFPMLabel);
            this.Controls.Add(requiredMaxFPMTextBox);
            this.Controls.Add(minBendRadiusLabel);
            this.Controls.Add(minBendRadiusTextBox);
            this.Controls.Add(minLoopLengthLabel);
            this.Controls.Add(minLoopLengthTextBox);
            this.Controls.Add(coilODLabel);
            this.Controls.Add(coilODTextBox);
            this.Controls.Add(coilIDLabel);
            this.Controls.Add(coilIDTextBox);
            this.Controls.Add(processButton);
        }

        private void ProcessInformation(
            string customer,
            string date,
            string reference,
            string coilWidth,
            string coilWeight,
            string materialThickness,
            string materialType,
            string yieldStrength,
            string materialTensile,
            string requiredMaxFPM,
            string minBendRadius,
            string minLoopLength,
            string coilOD,
            string coilID)
        {
            ResultForm resultForm = new ResultForm(
                customer,
                date,
                reference,
                coilWidth,
                coilWeight,
                materialThickness,
                materialType,
                yieldStrength,
                materialTensile,
                requiredMaxFPM,
                minBendRadius,
                minLoopLength,
                coilOD,
                coilID
            );
            resultForm.Show();
        }

        private void OpenTableOfContents()
        {
            TableOfContentsForm tocForm = new TableOfContentsForm();
            tocForm.Show();
        }

        private void OpenMaterialSpecifications()
        {
            MaterialSpecificationsForm materialSpecsForm = new MaterialSpecificationsForm();
            materialSpecsForm.Show();
        }

        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }
}
