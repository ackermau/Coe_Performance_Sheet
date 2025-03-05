using System;
using System.Windows.Forms;

namespace RFQForm
{
    public partial class TableOfContentsForm : Form
    {
        public TableOfContentsForm()
        {
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            this.Text = "Table of Contents";
            this.Size = new System.Drawing.Size(400, 600);

            // Create buttons for each section
            Button rfqButton = new Button() { Text = "RFQ", Location = new System.Drawing.Point(10, 10) };
            rfqButton.Click += (sender, e) => OpenForm(new MainForm());

            Button materialSpecsButton = new Button() { Text = "Material Specifications", Location = new System.Drawing.Point(10, 40) };
            materialSpecsButton.Click += (sender, e) => OpenForm(new MaterialSpecificationsForm());

            // Add more buttons for other sections as needed...

            // Add buttons to the form
            this.Controls.Add(rfqButton);
            this.Controls.Add(materialSpecsButton);
            // Add more buttons to the form...
        }

        private void OpenForm(Form form)
        {
            form.Show();
        }
    }
}
