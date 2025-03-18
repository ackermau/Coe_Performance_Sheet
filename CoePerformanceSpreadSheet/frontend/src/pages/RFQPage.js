import { useState } from "react";
import { Button, TextField, Select, MenuItem, FormControl, InputLabel } from "@mui/material";

export default function RFQPage() {
    const [rfq, setRFQ] = useState({
        customer_name: "",
        project_name: "",
        line_type: "",
        material_type: "",
        thickness: "",
        width: "",
        speed: ""
    });

    const createRFQ = async () => {
        const response = await fetch("/api/rfq/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(rfq),
        });
        const data = await response.json();
        console.log("RFQ Created:", data);
    };

    return (
        <div className="p-4">
            <h1 className="text-xl font-bold">Request for Quote (RFQ)</h1>
            <p>For COE to provide the best recommendation for your line, please complete the details below.</p>

            <div className="grid grid-cols-2 gap-4">
                <TextField
                    label="Customer Name"
                    value={rfq.customer_name}
                    onChange={(e) => setRFQ({ ...rfq, customer_name: e.target.value })}
                    fullWidth
                />
                <TextField
                    label="Project Name"
                    value={rfq.project_name}
                    onChange={(e) => setRFQ({ ...rfq, project_name: e.target.value })}
                    fullWidth
                />
            </div>

            <h2 className="text-lg font-semibold mt-4">Line Specifications</h2>
            <div className="grid grid-cols-2 gap-4">
                <FormControl fullWidth>
                    <InputLabel>Line Type</InputLabel>
                    <Select
                        value={rfq.line_type}
                        onChange={(e) => setRFQ({ ...rfq, line_type: e.target.value })}
                    >
                        <MenuItem value="Slitting">Slitting</MenuItem>
                        <MenuItem value="Cut-to-Length">Cut-to-Length</MenuItem>
                        <MenuItem value="Coil Processing">Coil Processing</MenuItem>
                    </Select>
                </FormControl>
                <TextField
                    label="Material Type"
                    value={rfq.material_type}
                    onChange={(e) => setRFQ({ ...rfq, material_type: e.target.value })}
                    fullWidth
                />
                <TextField
                    label="Thickness (in)"
                    type="number"
                    value={rfq.thickness}
                    onChange={(e) => setRFQ({ ...rfq, thickness: e.target.value })}
                    fullWidth
                />
                <TextField
                    label="Width (in)"
                    type="number"
                    value={rfq.width}
                    onChange={(e) => setRFQ({ ...rfq, width: e.target.value })}
                    fullWidth
                />
                <TextField
                    label="Speed (FPM)"
                    type="number"
                    value={rfq.speed}
                    onChange={(e) => setRFQ({ ...rfq, speed: e.target.value })}
                    fullWidth
                />
            </div>

            <Button onClick={createRFQ} className="mt-4" variant="contained" color="primary">Submit RFQ</Button>
        </div>
    );
}
