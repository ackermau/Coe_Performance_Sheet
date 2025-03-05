using System;
using System.Windows.Forms;

namespace RFQForm
{
    public partial class ResultForm : Form
    {
        public ResultForm(
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
            InitializeComponent();

            // Display the information
            Label resultLabel = new Label()
            {
                Text = $"Customer: {customer}\nDate: {date}\nReference: {reference}\nCoil Width: {coilWidth}\nCoil Weight: {coilWeight}\nMaterial Thickness: {materialThickness}\nMaterial Type: {materialType}\nYield Strength: {yieldStrength}\nMaterial Tensile: {materialTensile}\nRequired Maximum FPM: {requiredMaxFPM}\nMinimum Bend Radius: {minBendRadius}\nMin Loop Length: {minLoopLength}\nCoil O.D.: {coilOD}\nCoil I.D.: {coilID}",
                Location = new System.Drawing.Point(10, 10),
                Size = new System.Drawing.Size(760, 540)
            };

            this.Controls.Add(resultLabel);
        }

        private void InitializeComponent()
        {
            this.Text = "RFQ Result";
            this.Size = new System.Drawing.Size(800, 600);
        }
    }
}
