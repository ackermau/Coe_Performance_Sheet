import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";
import { RFQFormProvider } from "./context/RFQFormContext";
import { MaterialSpecsProvider } from "./context/MaterialSpecsContext";
import { TddbhdProvider } from "./context/TddbhdContext";
import { ReelDriveProvider } from "./context/ReelDriveContext";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <BrowserRouter>
            <RFQFormProvider>
                <MaterialSpecsProvider>
                    <ReelDriveProvider>
                        <TddbhdProvider>
                            <App />
                        </TddbhdProvider>
                    </ReelDriveProvider>
                </MaterialSpecsProvider>
            </RFQFormProvider>
        </BrowserRouter>
    </React.StrictMode>
);