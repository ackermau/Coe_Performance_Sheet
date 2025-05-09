import { useState, useEffect, useContext } from 'react';
import { Paper, Typography, Grid, Button } from '@mui/material';
import { API_URL } from '../../config';
import { MaterialContext } from '../../context/MaterialContext';

const formatLabel = (label) => {
    const suffixes = ["Max", "Min", "Full", "Width"];
    const suffixRegex = new RegExp(`(${suffixes.join("|")})$`, "i");

    // Remove suffix if present
    const stripped = label.replace(suffixRegex, "");

    // Then apply formatting
    return stripped
        .replace(/_/g, " ")
        .replace(/\b\w/g, (char) => char.toUpperCase())
        .replace(/([a-z])([A-Z])/g, "$1 $2")
        .trim();
};

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

const baseFields = [
    "coilWidth", "materialThickness", "materialYieldStrength", "materialType", "straightenerModel"
];

const calculatedFields = [
    "rollDia", "centDist", "modulus", "jackForceAvailable", 
];

pageMapping = { page1: "max", page2: "full", page3: "min", page4: "width" };

const groupFields = {
    max: [...baseFields.map(f => `${f}Max`), ...calculatedFields.map(f => `${f}Max`)],
    full: [...baseFields.map(f => `${f}Full`), ...calculatedFields.map(f => `${f}Full`)],
    min: [...baseFields.map(f => `${f}Min`), ...calculatedFields.map(f => `${f}Min`)],
    width: [...baseFields.map(f => `${f}Width`), ...calculatedFields.map(f => `${f}Width`)]
};

const CalculatedField = ({ label, value }) => (
    <>
        <Grid item xs={6} sm={4}>
            <Typography variant="body1">{label}</Typography>
        </Grid>
        <Grid item xs={6} sm={8}>
            <TextField
                value={value}
                variant="outlined"
                size="small"
                fullWidth
                InputProps={{ readOnly: true }}
            />
        </Grid>
    </>
);

export default function RollsSevenRollStrBackbend() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const { materialSpecs } = useContext(MaterialContext);
    const { subpageData, setSubpageData, activePage, setActivePage } = useContext()

    const getDefaultDataForGroup = (group, materialSpecs) => {
        return {
            ...Object.fromEntries(
                groupFields[group].map(f => [f, materialSpecs[f] || ""])
            )
        };
    };

    useEffect(() => {

    }, []);

    const handleChange = (field, value) => {
        
    };

    const triggerBackendCalculation = async () => {

    };

    if (loading) return <div>Loading...</div>;

    return (
        <Paper elevation={3} style={{ padding: '20px' }}>
            <Typography variant="h4" gutterBottom>
                7 Roll Straightener Backbend
            </Typography>
            
        </Paper>
    );
}