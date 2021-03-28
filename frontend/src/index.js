import React from "react"
import { SnackbarProvider } from "notistack"
import { BrowserRouter as Router, Route } from "react-router-dom"
import ReactDOM from "react-dom"
import "./index.css"
import App from "./App"
import Profile from "./user/profile"
import SignIn from "./user/signin"
import SignOut from "./user/signout"
import SignUp from "./user/signup"
import TOTPVerification from "./user/totp_verification"
import AuthenticationSettings from "./user/authentication_settings"
import NeedsApproval from "./user/needs-approval"
import SavedNews from "./news/saved_news"
import * as serviceWorker from "./serviceWorker"
import ManageSubscriptions from "./user/manage_subscriptions/manage_subscriptions"
import ReadNews from "./ReadNews"
import { TokenBasedAuthenticator } from "./WithAuthHandling"

export const AuthHandling = React.createContext(new TokenBasedAuthenticator())

ReactDOM.render(
    <Router>
        <SnackbarProvider maxSnack={3} autoHideDuration={2000} anchorOrigin={{ vertical: "top", horizontal: "right" }}>
            <Route exact path="/" component={App} />
            <Route exact path="/read-news" component={ReadNews} />
            <Route exact path="/saved-news" component={SavedNews} />
            <Route exact path="/user/signin" component={SignIn} />
            <Route exact path="/user/signout" component={SignOut} />
            <Route exact path="/user/signup" component={SignUp} />
            <Route exact path="/user/totp-verification" component={TOTPVerification} />
            <Route exact path="/user/authentication-settings" component={AuthenticationSettings} />
            <Route exact path="/user/profile" component={Profile} />
            <Route exact path="/user/needs-approval" component={NeedsApproval} />
            <Route exact path="/user/manage-subscriptions" component={ManageSubscriptions} />
        </SnackbarProvider>
    </Router>,
    document.getElementById("root")
)

serviceWorker.unregister()
