import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";
import { RFQFormProvider } from "./context/RFQFormContext";
import { MaterialSpecsProvider } from "./context/MaterialSpecsContext";
import { TddbhdProvider } from "./context/TddbhdContext";
import { ReelDriveProvider } from "./context/ReelDriveContext";
import { StrUtilityProvider } from "./context/StrUtilityContext";
import { SevenRollStrBackbendProvider } from "./context/Rolls/sevenRollStrBackbendContext";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <BrowserRouter>
            <RFQFormProvider>
                <MaterialSpecsProvider>
                    <ReelDriveProvider>
                        <TddbhdProvider>
                            <StrUtilityProvider>
                                <SevenRollStrBackbendProvider>
                                    <App />
                                </SevenRollStrBackbendProvider>
                            </StrUtilityProvider>
                        </TddbhdProvider>
                    </ReelDriveProvider>
                </MaterialSpecsProvider>
            </RFQFormProvider>
        </BrowserRouter>
    </React.StrictMode>
);