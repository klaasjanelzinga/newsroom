import React from 'react';
import { SnackbarProvider } from 'notistack';
import { BrowserRouter as Router, Route } from "react-router-dom";
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import profile from './user/profile';
import signin from './user/signin';
import signout from './user/signout';
import needsApproval from './user/needs-approval';
import * as serviceWorker from './serviceWorker';

ReactDOM.render(
    <Router>
        <SnackbarProvider
            maxSnack={3}
            autoHideDuration={2000}
            anchorOrigin={{ vertical: 'top', horizontal: 'right', }}>
            <Route exact path="/" component={App} />
            <Route exact path="/user/signin" component={signin} />
            <Route exact path="/user/signout" component={signout} />
            <Route exact path="/user/profile" component={profile} />
            <Route exact path="/user/needs-approval" component={needsApproval} />
        </SnackbarProvider>
    </Router>
    ,
    document.getElementById('root')
);

serviceWorker.unregister();
