import { useState, useEffect, useContext } from 'react';
import { useLocation } from 'react-router-dom';
import { Paper, Typography, Grid, Button, Box, ToggleButtonGroup, ToggleButton, Divider, TextField, FormControl, Select } from '@mui/material';
import { API_URL } from '../../config';
import { StrUtilityContext } from '../../context/StrUtilityContext';
import { SevenRollStrBackbendContext } from '../../context/Rolls/sevenRollStrBackbendContext';

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
    "coilWidth", "materialThickness", "yieldStrength", "materialType", "strModel", "numStrRolls"
];

const calculatedFields = [
    "rollDia", "centDist", "modulus", "jackForceAvailable", "maxRollDepthWithoutMaterial", "maxRollDepthWithMaterial", "rollerDepthRequired", 
    "rollerDepthRequiredCheck", "rollHeightFirstUp", "rollHeightMidUp", "rollHeightLast", 
    "resRadFirstUp", "resRadFirstDown", "resRadMidUp", "resRadMidDown", "resRadLast", "rRiFirstUp", "rRiFirstDown", "rRiMidUp", "rRiMidDown", "rRiLast",
    "mbFirstUp", "mbFirstDown", "mbMidUp", "mbMidDown", "mbLast", "mbMyFirstUp", "mbMyFirstDown", "mbMyMidUp", "mbMyMidDown", "mbMyLast",
    "springbackFirstUp", "springbackFirstDown", "springbackMidUp", "springbackMidDown", "springbackLast", "radiusAfterSpringbackFirstUp",
    "radiusAfterSpringbackFirstDown", "radiusAfterSpringbackMidUp", "radiusAfterSpringbackMidDown", "radiusAfterSpringbackLast",
    "forceRequiredFirstUp", "forceRequiredMidUp", "forceRequiredLast",
    "percentYieldFirstUp", "percentYieldFirstDown", "percentYieldMidUp", "percentYieldMidDown", "percentYieldLast",
    "numberOfYieldStrainsFirstUp", "numberOfYieldStrainsMidUp", "numberOfYieldStrainsLast"
];

const pageMapping = { page1: "max", page2: "full", page3: "min", page4: "width" };

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
    const { subpageData: strUtility } = useContext(StrUtilityContext);
    const { subpageData, setSubpageData, activePage, setActivePage } = useContext(SevenRollStrBackbendContext)
    const location = useLocation();

    const getDefaultDataForGroup = (group, strUtility) => {
        return {
            ...Object.fromEntries(
                groupFields[group].map(f => [f, strUtility[f] || ""])
            )
        };
    };

    useEffect(() => {
        const updateDataAndTriggerCalculations = async () => {
            if (!activePage || !strUtility) return;
            setSubpageData(prev => {
                const newData = {
                    page1: { ...getDefaultDataForGroup("max", strUtility), ...prev.page1 },
                    page2: { ...getDefaultDataForGroup("full", strUtility), ...prev.page2 },
                    page3: { ...getDefaultDataForGroup("min", strUtility), ...prev.page3 },
                    page4: { ...getDefaultDataForGroup("width", strUtility), ...prev.page4 }
                };
                return JSON.stringify(prev) !== JSON.stringify(newData) ? newData : prev;
            });
        };

        updateDataAndTriggerCalculations();
    }, [activePage, strUtility]);

    useEffect(() => {
        if (
            location.pathname === "/sevenrollstr" &&
            strUtility &&
            Object.keys(strUtility).length > 0
        ) {
            try {
                Object.keys(subpageData).forEach(pageKey => {
                    console.log("subpageData: ", subpageData);
                    const payload = buildSevenRollPayload(subpageData, pageKey);
                    console.log("Payload for backend calculation: ", payload);
                    triggerBackendCalculation(payload, pageKey);
                });
            } catch (error) {
                console.error("Error in triggerBackendCalculation: ", error);
            }
        }
    }, [location, strUtility]);

    const snakeToCamel = (str) => {
        return str.split('_').map((word, index) => {
            if (index === 0) return word;
            return knownAcronyms.includes(word.toLowerCase())
                ? word.toUpperCase()
                : word.charAt(0).toUpperCase() + word.slice(1);
        }).join('');
    };

    const buildSevenRollPayload = (subpageData, pageKey) => {
        const capSuffix = capitalize(pageMapping[pageKey]);
        const data = subpageData[pageKey];
        return {
            yield_strength: parseFloat(data[`yieldStrength${capSuffix}`]),
            thickness: parseFloat(data[`materialThickness${capSuffix}`]),
            width: parseFloat(data[`coilWidth${capSuffix}`]),
            material_type: data[`materialType${capSuffix}`],
            str_model: data[`strModel${capSuffix}`],
            num_str_rolls: data.numStrRolls,
        };
    };

    const triggerBackendCalculation = async (payload, pageKey) => {
        try {
            const response = await fetch(`${API_URL}/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                const errorData = await response.json();
                console.error("Backend response data: ", errorData);
                return;
            }
            const result = await response.json();
            const capSuffix = capitalize(pageMapping[activePage]);
            console.log("Backend calculation result: ", result);
            const transformedData = {};
            for (const key in result) {
                const camelKey = snakeToCamel(key);
                transformedData[`${camelKey}${capSuffix}`] = result[key];
            }
            console.log("Transformed data: ", transformedData);
            setSubpageData(prev => ({
                ...prev,
                [activePage]: {
                    ...prev[activePage],
                    ...transformedData
                }
            }));
        } catch (error) {
            console.error("Error during backend calculation: ", error);
        }
    };

    const pages = [
        { key: "page1", title: "Max" },
        { key: "page2", title: "Full" },
        { key: "page3", title: "Min" },
        { key: "page4", title: "Width" }
    ];

    const goToPreviousPage = () => {
        const currentIndex = pages.findIndex((page) => page.key === activePage);
        if (currentIndex > 0) setActivePage(pages[currentIndex - 1].key);
    };

    const goToNextPage = () => {
        const currentIndex = pages.findIndex((page) => page.key === activePage);
        if (currentIndex < pages.length - 1) setActivePage(pages[currentIndex + 1].key);
    };

    const currentGroup = pageMapping[activePage];
    const currentGroupFields = groupFields[currentGroup];

    // If loading, show loading text
    // if (loading) return <div>Loading...</div>;
    
    return (
        <Paper elevation={3} style={{ padding: '20px' }}>
            <Typography variant="h4" gutterBottom>
                7 Roll Straightener Backbend
            </Typography>

            {/* Calculated Fields */}
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6">Calculated Values</Typography>
            <Grid container spacing={1} sx={{ mt: 1 }}>
                <Grid item xs={12} md={6}>
                    <Typography noWrap style={{ minWidth: 200 }}>Max Coil Weight</Typography>
                    <TextField size="small"
                        value={subpageData[activePage].maxCoilWeight || ""}
                        onChange={(e) => handleChange("maxCoilWeight", e.target.value)}
                        name="maxCoilWeight"
                        type="number"
                        disabled={true}
                    />
                </Grid>

                {currentGroupFields.map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        <CalculatedField
                            label={formatLabel(field)}
                            value={subpageData[activePage][field] || ""} />
                    </Grid>
                ))}
            </Grid>

            {/* Navigation Buttons */}
            <Grid
                container
                spacing={2}
                justifyContent="space-between"
                alignItems="center"
                sx={{ mt: 4 }}
            >
                <Grid item>
                    <Button
                        variant="contained"
                        onClick={goToPreviousPage}
                        disabled={activePage === "page1"}
                    >
                        Back
                    </Button>
                </Grid>
                <Grid item>
                    <Typography variant="subtitle1">
                        {pages.find((p) => p.key === activePage)?.title}
                    </Typography>
                </Grid>
                <Grid item>
                    <Button
                        variant="contained"
                        onClick={goToNextPage}
                        disabled={activePage === "page4"}
                    >
                        Next
                    </Button>
                </Grid>
            </Grid>
        </Paper>
    );
}