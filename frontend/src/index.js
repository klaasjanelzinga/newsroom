import React from 'react';
import {SnackbarProvider} from 'notistack';
import {BrowserRouter as Router, Route} from "react-router-dom";
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import Profile from './user/profile';
import Signin from './user/signin';
import Signout from './user/signout';
import NeedsApproval from './user/needs-approval';
import * as serviceWorker from './serviceWorker';
import ManageSubscriptions from "./user/manage_subscriptions/manage_subscriptions";
import ReadNews from "./ReadNews";
import {GoogleAuthHandling} from "./GoogleAuthHandling";

export const AuthHandling = React.createContext(new GoogleAuthHandling())

ReactDOM.render(
    <Router>
        <SnackbarProvider
            maxSnack={3}
            autoHideDuration={2000}
            anchorOrigin={{vertical: 'top', horizontal: 'right',}}>
            <Route exact path="/" component={App}/>
            <Route exact path="/read-news" component={ReadNews}/>
            <Route exact path="/user/signin" component={Signin}/>
            <Route exact path="/user/signout" component={Signout}/>
            <Route exact path="/user/profile" component={Profile}/>
            <Route exact path="/user/needs-approval" component={NeedsApproval}/>
            <Route exact path="/user/manage-subscriptions" component={ManageSubscriptions}/>
        </SnackbarProvider>
    </Router>
    ,
    document.getElementById('root')
);

serviceWorker.unregister();
