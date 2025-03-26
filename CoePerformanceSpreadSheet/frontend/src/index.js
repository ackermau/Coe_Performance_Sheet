import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";
import { RFQFormProvider } from "./context/RFQFormContext";
import { MaterialSpecsProvider } from "./context/MaterialSpecsContext";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <BrowserRouter>
            <RFQFormProvider>
                <MaterialSpecsProvider>
                    <App />
                </MaterialSpecsProvider>
            </RFQFormProvider>
        </BrowserRouter>
    </React.StrictMode>
);