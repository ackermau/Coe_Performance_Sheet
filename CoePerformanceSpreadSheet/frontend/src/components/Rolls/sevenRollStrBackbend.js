import { useState, useEffect, useContext } from 'react';
import { Paper, Typography, Grid, Button } from '@mui/material';
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
    "coilWidth", "materialThickness", "materialYieldStrength", "materialType", "straightenerModel"
];

const calculatedFields = [
    "rollDia", "centDist", "modulus", "jackForceAvailable", 
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
    const { strUtility } = useContext(StrUtilityContext);
    const { subpageData, setSubpageData, activePage, setActivePage } = useContext(SevenRollStrBackbendContext)

    const getDefaultDataForGroup = (group, sharedDefaults, strUtility) => {
        return {
            ...sharedDefaults,
            ...Object.fromEntries(
                groupFields[group].map(f => [f, strUtility[f] || ""])
            )
        };
    };

    useEffect(() => {
        const updateDataAndTriggerCalculations = async () => {
            if (!activePage || !strUtility) return;

            const sharedDefaults = {
                coilWidth: strUtility.coilWidth,
                materialThickness: strUtility.materialThickness,
                materialYieldStrength: strUtility.materialYieldStrength,
                materialType: strUtility.materialType,
                straightenerModel: strUtility.straightenerModel
            };

            setSubpageData(prev => {
                const newData = {
                    page1: { ...getDefaultDataForGroup("max", sharedDefaults, strUtility), ...prev.page1 },
                    page2: { ...getDefaultDataForGroup("full", sharedDefaults, strUtility), ...prev.page2 },
                    page3: { ...getDefaultDataForGroup("min", sharedDefaults, strUtility), ...prev.page3 },
                    page4: { ...getDefaultDataForGroup("width", sharedDefaults, strUtility), ...prev.page4 }
                };
                return JSON.stringify(prev) !== JSON.stringify(newData) ? newData : prev;
            });
        };

        updateDataAndTriggerCalculations();
    }, [activePage, strUtility]);

    const handleChange = (field, value) => {
        setSubpageData(prev => {
            const updatedData = { ...prev };

            if (sharedFields.includes(field)) {
                Object.keys(prev).forEach(pageKey => {
                    updatedData[pageKey] = {
                        ...prev[pageKey],
                        [field]: value
                    };
                });
            } else {
                updatedData[activePage] = {
                    ...prev[activePage],
                    [field]: value
                };
            }

            try {
                Object.keys(updatedData).forEach(pageKey => {
                    const payload = buildSevenRollPayload(updatedData, pageKey);
                    console.log("Payload for backend calculation: ", payload);
                    triggerBackendCalculation(payload, pageKey);
                });
            } catch (error) {
                console.error("Error in handleChange: ", error);
            }

            return updatedData;
        });
    };

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
            yield_strength: parseFloat(data.yield_strength),
            thickness: parseFloat(data.materialThickness),
            width: parseFloat(data.coilWidth),
            material_type: data.materialType,
            straightener_model: data.straightenerModel,
        };
    };

    const triggerBackendCalculation = async (payload, pageKey) => {
        try {
            const response = await fetch(`${API_URL}/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
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

    // If loading, show loading text
    if (loading) return <div>Loading...</div>;

    // Determine current active page's data and suffix
    const currentData = subpageData?.[activePage] || {};
    const suffix = capitalize(pageMapping[activePage] || "");

    // Keys to skip (input fields with or without suffix)
    const skipKeys = [
        ...baseFields,
        ...baseFields.map(f => f + suffix)
    ];

    // Prepare shared variables (known single-value outputs)
    const sharedKeys = [
        `rollDiameter${suffix}`,
        `centerDistance${suffix}`,
        `jackForceAvailable${suffix}`,
        `maxRollDepthWithoutMaterial${suffix}`,
        `maxRollDepthWithMaterial${suffix}`,
        `rollerDepthRequired${suffix}`
    ];
    const sharedRows = sharedKeys
        .filter(key => currentData[key] !== undefined && currentData[key] !== "")
        .map(key => ({
            label: formatLabel(key),
            value: currentData[key]
        }));

    // Prepare roller table data grouped by position
    const rollerPositions = [
        { id: "firstUp", label: "First Up" },
        { id: "firstDown", label: "First Down" },
        { id: "midUp", label: "Mid Up" },
        { id: "midDown", label: "Mid Down" },
        { id: "last", label: "Last" }
    ];
    const rollerRows = {
        firstUp: {},
        firstDown: {},
        midUp: {},
        midDown: {},
        last: {}
    };

    const remainingKeys = [];
    // Loop through all keys in currentData to distribute them
    for (const key of Object.keys(currentData)) {
        if (skipKeys.includes(key)) continue; // skip input fields
        const value = currentData[key];
        if (value === undefined || value === "") continue; // skip missing values
        // Remove suffix from key for grouping and labeling
        const keyBase = key.endsWith(suffix) ? key.slice(0, -suffix.length) : key;
        if (keyBase.includes("FirstUp")) {
            const metric = keyBase.replace("FirstUp", "");
            rollerRows.firstUp[metric] = value;
        } else if (keyBase.includes("FirstDown")) {
            const metric = keyBase.replace("FirstDown", "");
            rollerRows.firstDown[metric] = value;
        } else if (keyBase.includes("MidUp")) {
            const metric = keyBase.replace("MidUp", "");
            rollerRows.midUp[metric] = value;
        } else if (keyBase.includes("MidDown")) {
            const metric = keyBase.replace("MidDown", "");
            rollerRows.midDown[metric] = value;
        } else if (keyBase.includes("Last")) {
            const metric = keyBase.replace("Last", "");
            rollerRows.last[metric] = value;
        } else if (
            // Handle special keys without explicit up/down in name
            (keyBase.endsWith("First") || keyBase.endsWith("Mid") || keyBase.endsWith("Last")) &&
            (keyBase.startsWith("rollHeight") || keyBase.startsWith("forceRequired") || keyBase.startsWith("numberOfYieldStrains"))
        ) {
            if (keyBase.endsWith("First")) {
                const metric = keyBase.replace("First", "");
                rollerRows.firstUp[metric] = value;
            } else if (keyBase.endsWith("Mid")) {
                const metric = keyBase.replace("Mid", "");
                rollerRows.midUp[metric] = value;
            } else if (keyBase.endsWith("Last")) {
                const metric = keyBase.replace("Last", "");
                rollerRows.last[metric] = value;
            }
        } else {
            // If not matched above, treat as remaining output
            remainingKeys.push(key);
        }
    }

    // Prepare remaining calculated values rows (exclude any empties)
    const remainingRows = remainingKeys
        .filter(key => currentData[key] !== undefined && currentData[key] !== "")
        .map(key => ({
            label: formatLabel(key),
            value: currentData[key]
        }));

    // Determine roller table metrics (columns) present
    const allMetrics = new Set();
    Object.values(rollerRows).forEach(metricsObj => {
        Object.keys(metricsObj).forEach(metric => allMetrics.add(metric));
    });
    const orderedMetrics = [
        "rollHeight", "resRad", "rRi", "mb", "mbMy",
        "springback", "radiusAfterSpringback", "forceRequired",
        "percentYield", "numberOfYieldStrains"
    ];
    const presentMetrics = orderedMetrics.filter(metric => allMetrics.has(metric));

    return (
        <Paper elevation={3} style={{ padding: '20px' }}>
            <Typography variant="h4" gutterBottom>
                7 Roll Straightener Backbend
            </Typography>

            {/* Toggle buttons for subpages */}
            <Box sx={{ mb: 2 }}>
                <ToggleButtonGroup
                    value={activePage}
                    exclusive
                    onChange={(event, newPage) => { if (newPage) setActivePage(newPage); }}
                    size="small"
                >
                    <ToggleButton value="page1">Max</ToggleButton>
                    <ToggleButton value="page2">Full</ToggleButton>
                    <ToggleButton value="page3">Min</ToggleButton>
                    <ToggleButton value="page4">Width</ToggleButton>
                </ToggleButtonGroup>
            </Box>

            {/* Shared Variables Table */}
            <Typography variant="h6" gutterBottom>Shared Variables</Typography>
            <Table size="small">
                <TableBody>
                    {sharedRows.map((row, idx) => (
                        <TableRow key={idx}>
                            <TableCell>{row.label}</TableCell>
                            <TableCell>{row.value}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>

            {/* Roller Table */}
            <Typography variant="h6" gutterBottom style={{ marginTop: '16px' }}>Roller Table</Typography>
            <Box sx={{ overflowX: 'auto' }}>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Position</TableCell>
                            {presentMetrics.map((metric, idx) => (
                                <TableCell key={idx}>{formatLabel(metric)}</TableCell>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {rollerPositions.map(pos => {
                            const metricsObj = rollerRows[pos.id];
                            // Skip positions with no data at all
                            if (!metricsObj || Object.keys(metricsObj).length === 0) return null;
                            return (
                                <TableRow key={pos.id}>
                                    <TableCell>{pos.label}</TableCell>
                                    {presentMetrics.map((metric, idx) => (
                                        <TableCell key={idx}>
                                            {metricsObj[metric] !== undefined ? metricsObj[metric] : ""}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </Box>

            {/* Remaining Calculated Values Table */}
            {remainingRows.length > 0 && (
                <>
                    <Typography variant="h6" gutterBottom style={{ marginTop: '16px' }}>
                        Remaining Calculated Values
                    </Typography>
                    <Table size="small">
                        <TableBody>
                            {remainingRows.map((row, idx) => (
                                <TableRow key={idx}>
                                    <TableCell>{row.label}</TableCell>
                                    <TableCell>{row.value}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </>
            )}
        </Paper>
    );
}