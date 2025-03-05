using System;
using System.Windows.Forms;

namespace RFQForm
{
    public partial class MaterialSpecificationsForm : Form
    {
        public MaterialSpecificationsForm()
        {
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            this.Text = "Material Specifications";
            this.Size = new System.Drawing.Size(800, 600);

            // Customer Information
            Label customerLabel = new Label() { Text = "Customer", Location = new System.Drawing.Point(10, 10) };
            TextBox customerTextBox = new TextBox() { Location = new System.Drawing.Point(150, 10) };

            Label dateLabel = new Label() { Text = "Date", Location = new System.Drawing.Point(10, 40) };
            TextBox dateTextBox = new TextBox() { Location = new System.Drawing.Point(150, 40) };

            Label referenceLabel = new Label() { Text = "Reference", Location = new System.Drawing.Point(10, 70) };
            TextBox referenceTextBox = new TextBox() { Location = new System.Drawing.Point(150, 70) };

            // Material Specifications
            Label coilWidthLabel = new Label() { Text = "Coil Width (in)", Location = new System.Drawing.Point(10, 100) };
            TextBox coilWidthTextBox = new TextBox() { Location = new System.Drawing.Point(150, 100) };

            Label coilWeightLabel = new Label() { Text = "Coil Weight", Location = new System.Drawing.Point(10, 130) };
            TextBox coilWeightTextBox = new TextBox() { Location = new System.Drawing.Point(150, 130) };

            Label materialThicknessLabel = new Label() { Text = "Material Thickness (in)", Location = new System.Drawing.Point(10, 160) };
            TextBox materialThicknessTextBox = new TextBox() { Location = new System.Drawing.Point(150, 160) };

            Label materialTypeLabel = new Label() { Text = "Material Type", Location = new System.Drawing.Point(10, 190) };
            TextBox materialTypeTextBox = new TextBox() { Location = new System.Drawing.Point(150, 190) };

            Label yieldStrengthLabel = new Label() { Text = "Yield Strength (psi)", Location = new System.Drawing.Point(10, 220) };
            TextBox yieldStrengthTextBox = new TextBox() { Location = new System.Drawing.Point(150, 220) };

            Label materialTensileLabel = new Label() { Text = "Material Tensile (psi)", Location = new System.Drawing.Point(10, 250) };
            TextBox materialTensileTextBox = new TextBox() { Location = new System.Drawing.Point(150, 250) };

            Label requiredMaxFPMLabel = new Label() { Text = "Required Maximum FPM", Location = new System.Drawing.Point(10, 280) };
            TextBox requiredMaxFPMTextBox = new TextBox() { Location = new System.Drawing.Point(150, 280) };

            Label minBendRadiusLabel = new Label() { Text = "Minimum Bend Radius (in)", Location = new System.Drawing.Point(10, 310) };
            TextBox minBendRadiusTextBox = new TextBox() { Location = new System.Drawing.Point(150, 310) };

            Label minLoopLengthLabel = new Label() { Text = "Min Loop Length (ft)", Location = new System.Drawing.Point(10, 340) };
            TextBox minLoopLengthTextBox = new TextBox() { Location = new System.Drawing.Point(150, 340) };

            Label coilODLabel = new Label() { Text = "Coil O.D.", Location = new System.Drawing.Point(10, 370) };
            TextBox coilODTextBox = new TextBox() { Location = new System.Drawing.Point(150, 370) };

            Label coilIDLabel = new Label() { Text = "Coil I.D.", Location = new System.Drawing.Point(10, 400) };
            TextBox coilIDTextBox = new TextBox() { Location = new System.Drawing.Point(150, 400) };

            Label coilODCalculatedLabel = new Label() { Text = "Coil O.D. Calculated", Location = new System.Drawing.Point(10, 430) };
            TextBox coilODCalculatedTextBox = new TextBox() { Location = new System.Drawing.Point(150, 430) };

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
            this.Controls.Add(coilODCalculatedLabel);
            this.Controls.Add(coilODCalculatedTextBox);
        }
    }
}
