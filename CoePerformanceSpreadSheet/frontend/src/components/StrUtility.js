import { useState, useEffect, useContext } from "react";
import {
    Paper, Typography, Grid, Divider, TextField, FormControl, Select, MenuItem, Button, Table, TableBody, TableRow, TableCell, CircularProgress
} from "@mui/material";
import { API_URL } from '../config';
import { StrUtilityContext } from "../context/StrUtilityContext";

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

const payoffOptions = [
    "TOP", "BOTTOM"
];

const strModelOptions = [
    "CPPS-250", "CPPS-306", "CPPS-350", "CPPS-406", "CPPS-507", "SPGPS-810"
];

const strWidthOptions = [
    42, 48, 54, 60, 66, 72, 78
];

const horsepowerOptions = [
    40, 50, 60, 75, 100, 125
];

const feedRateOptions = [
    80, 100, 120, 140, 160, 200
];

const autoBrakeCompenOptions = [
    "YES", "NO"
];

const pulledFields = [
    "coilWeightCap", "coilID", "coilWidth", "thickness", "materialType"
];

const lookupFields = [
    "strRollDia", "pinchRollDia", "centerDist", "jackForceAvailable", "maxRollDepth", "modulus",
    "pinchRollGearTeeth", "pinchRollGearDP", "strRollGearTeeth", "strRollGearDP", "faceWidthTeeth", "contAngleTeeth"
];

const calculatedFields = [
    "requiredForce", "pinchRoll", "strRoll", "horsepowerRequired", "actualCoilWeight", "coilOD", "strTorque", "accelerationTorque", "brakeTorque"
];

const groupFields = {
    max: [...pulledFields.map(field => `${field}Max`), ...lookupFields.map(field => `${field}Max`), ...calculatedFields.map(field => `${field}Max`)],
    full: [...pulledFields.map(field => `${field}Full`), ...lookupFields.map(field => `${field}Full`), ...calculatedFields.map(field => `${field}Full`)],
    min: [...pulledFields.map(field => `${field}Min`), ...lookupFields.map(field => `${field}Min`), ...lookupFields.map(field => `${field}Min`), ...calculatedFields.map(field => `${field}Min`)],
    width: [...pulledFields.map(field => `${field}Width`), ...lookupFields.map(field => `${field}Width`), ...calculatedFields.map(field => `${field}Width`)]
};

export default function StrUtility() {
    const { subpageData, setSubpageData, activePage, setActivePage } = StrUtilityContext();

    const suffix = pageMapping[activePage];
    const capSuffix = capitalize(suffix);
    const [loading, setLoading] = useState(false);

    const sharedDefaults = {
        payoff: payoffOptions[0],
        strModel: strModelOptions[0],
        strWidth: strWidthOptions[0],
        horsepower: horsepowerOptions[0],
        feedRate: feedRateOptions[0],
        autoBrakeCompensation: autoBrakeCompenOptions[0],
        acceleration: 1
    }

    const getDefaultDataForGroup = (group) => {
        return {
            ...Object.fromEntries(
                groupFields[group].map(field => [field, materialSpecs?.[f] || ""])
            )
        };
    }

    useEffect(() => {
        const updateDataAndTriggerCalculations = async () => {
            // Avoid triggering before data is ready
    }

    return (
        <Paper sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom>
                TB/DB/HD Machine Simulation - {`${capSuffix}`}
            </Typography>
            <Divider sx={{ my: 2 }} />

        </Paper>
    );
}