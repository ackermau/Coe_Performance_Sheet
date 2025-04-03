import { useEffect, useState, useContext } from "react";
import { RFQFormContext } from "../context/RFQFormContext";
import { MaterialSpecsContext } from "../context/MaterialSpecsContext";
import { Paper, Grid, Typography, Table, TableBody, TableCell, TableHead, TableRow, Divider } from "@mui/material";

export default function EquipmentSummary({ rfqId }) {
    const { rfqForm } = useContext(RFQFormContext);
    const { materialSpecs } = useContext(MaterialSpecsContext);
    const [rfq, setRFQ] = useState(null);

    useEffect(() => {
        const fetchRFQ = async () => {
            const response = await fetch(`/api/rfq/${rfqId}`);
            const data = await response.json();
            setRFQ(data);
        };
        fetchRFQ();
    }, [rfqId]);

    return (
        <Paper sx={{ padding: 4, margin: 2 }}>
            <Typography variant="h5" gutterBottom>
                Equipment Summary
            </Typography>

            <Divider sx={{ my: 2 }} />

            {/* Reel Section */}
            <Typography variant="h6">Reel</Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={4}><strong>Reel Model:</strong> CPR-200</Grid>
                <Grid item xs={4}><strong>Reel Width:</strong> 42</Grid>
                <Grid item xs={4}><strong>Backplate Diameter:</strong> 27</Grid>
                <Grid item xs={4}><strong>Reel Motorization:</strong> PullOff</Grid>
                <Grid item xs={4}><strong>Single or Double Ended:</strong> Single Ended</Grid>
                <Grid item xs={4}><strong>Air Clutch:</strong> Yes</Grid>
                <Grid item xs={4}><strong>Hyd. Threading Drive:</strong> 60 cu in (D-13374)</Grid>
                <Grid item xs={4}><strong>Hold Down Assy:</strong> XD</Grid>
                <Grid item xs={4}><strong>Hold Down Cylinder:</strong> 750</Grid>
                <Grid item xs={4}><strong>Brake Model:</strong> Failsafe - Double Stage</Grid>
                <Grid item xs={4}><strong>Brake Quantity:</strong> 1</Grid>
            </Grid>

            {/* Powered Straightener */}
            <Typography variant="h6">Powered Straightener</Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={4}><strong>Straightener Model:</strong> CPPS-507</Grid>
                <Grid item xs={4}><strong>Straightening Rolls:</strong> 7 Roll Str. Backbend</Grid>
                <Grid item xs={4}><strong>Backup Rolls:</strong> Not Required</Grid>
                <Grid item xs={4}><strong>Payoff:</strong> TOP</Grid>
                <Grid item xs={4}><strong>Str. Width (in):</strong> 42</Grid>
                <Grid item xs={4}><strong>Feed Rate (ft/min):</strong> 120</Grid>
                <Grid item xs={4}><strong>Acceleration (ft/sec):</strong> 1</Grid>
                <Grid item xs={4}><strong>Horsepower (HP):</strong> 50</Grid>
            </Grid>

            {/* Sigma 5 Feed Specs */}
            <Typography variant="h6">Sigma 5 Feed</Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={4}><strong>Application:</strong> Press Feed</Grid>
                <Grid item xs={4}><strong>Model:</strong> CPRF-S8</Grid>
                <Grid item xs={4}><strong>Machine Width:</strong> 42</Grid>
                <Grid item xs={4}><strong>Loop Pit:</strong> N</Grid>
                <Grid item xs={4}><strong>Full Width Rolls:</strong> Y</Grid>
                <Grid item xs={4}><strong>Feed Angle 1:</strong> 180</Grid>
                <Grid item xs={4}><strong>Feed Angle 2:</strong> 240</Grid>
                <Grid item xs={4}><strong>Press Bed Length:</strong> 48</Grid>
                <Grid item xs={4}><strong>Maximum Velocity ft/min:</strong> 282.75</Grid>
                <Grid item xs={4}><strong>Acceleration (ft/sec):</strong> 25</Grid>
                <Grid item xs={4}><strong>Ratio:</strong> 11.111</Grid>
                <Grid item xs={4}><strong>Feed Direction:</strong> L to R</Grid>
                <Grid item xs={4}><strong>Controls Level:</strong> SyncMaster</Grid>
                <Grid item xs={4}><strong>Type of line:</strong> Conventional</Grid>
                <Grid item xs={4}><strong>Passline:</strong> 55"</Grid>
                <Grid item xs={4}><strong>Light Gauge Non-Marking:</strong> NO</Grid>
                <Grid item xs={4}><strong>Non-Marking:</strong> Yes</Grid>
            </Grid>

            {/* Sigma 5 Feed Table */}
            <Table sx={{ mt: 2 }} size="small">
                <TableHead>
                    <TableRow>
                        <TableCell>Length</TableCell>
                        <TableCell>SPM @ 180 Deg.</TableCell>
                        <TableCell>FPM</TableCell>
                        <TableCell>SPM @ 240 Deg.</TableCell>
                        <TableCell>FPM</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    <TableRow><TableCell>10.66</TableCell><TableCell>72.82</TableCell><TableCell>64.68</TableCell><TableCell>97.09</TableCell><TableCell>86.24</TableCell></TableRow>
                    <TableRow><TableCell>4</TableCell><TableCell>112</TableCell><TableCell>37.33</TableCell><TableCell>150</TableCell><TableCell>50</TableCell></TableRow>
                    <TableRow><TableCell>8</TableCell><TableCell>82</TableCell><TableCell>54.67</TableCell><TableCell>110</TableCell><TableCell>73.33</TableCell></TableRow>
                    <TableRow><TableCell>12</TableCell><TableCell>68</TableCell><TableCell>68</TableCell><TableCell>91</TableCell><TableCell>91</TableCell></TableRow>
                    <TableRow><TableCell>16</TableCell><TableCell>59</TableCell><TableCell>78.67</TableCell><TableCell>78</TableCell><TableCell>104</TableCell></TableRow>
                    <TableRow><TableCell>20</TableCell><TableCell>51</TableCell><TableCell>85</TableCell><TableCell>69</TableCell><TableCell>115</TableCell></TableRow>
                    <TableRow><TableCell>24</TableCell><TableCell>46</TableCell><TableCell>92</TableCell><TableCell>60</TableCell><TableCell>120</TableCell></TableRow>
                </TableBody>
            </Table>
        </Paper>
    );
}
