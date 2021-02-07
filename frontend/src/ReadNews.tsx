import * as React from 'react';
import {createStyles, WithStyles, withStyles} from "@material-ui/core";
import './App.css';
import {Api} from "./Api"
import {withSnackbar, WithSnackbarProps} from "notistack";
import {RouteComponentProps} from "react-router";
import News, {NewsVariant} from "./news/news";
import {withRouter} from "react-router-dom";
import {withAuthHandling, WithAuthHandling} from "./WithAuthHandling";

const styles = createStyles({})

interface AppProps extends WithAuthHandling, RouteComponentProps, WithSnackbarProps, WithStyles<typeof styles> {
}

class ReadNews extends React.Component<AppProps> {

    apiFetch: Api

    constructor(props: AppProps) {
        super(props);
        this.apiFetch = new Api(props)
    }

    render(): JSX.Element {
        return <News variant={NewsVariant.READ_NEWS}/>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(ReadNews))))
