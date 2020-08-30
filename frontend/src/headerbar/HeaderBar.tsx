import * as React from 'react'
import {createStyles, withStyles, WithStyles} from "@material-ui/core";
import {RouteComponentProps, withRouter} from 'react-router-dom';
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Title from "./Title";
import AppMenu from "./AppMenu";
import HeaderMenu from "./HeaderMenu";

const styles = createStyles({
    headerbar: {
        width: '100%',
    },
    grow: {
        flexGrow: 1,
    }
});

export interface Props extends RouteComponentProps, WithStyles<typeof styles> {
}


const HeaderBar: React.FC<Props> = (props) => {
    const {classes} = props;
    return (
        <div className={classes.headerbar}>
            <AppBar position="static">
                <Toolbar>
                    <Title title={'=== News ==='}/>
                    <div className={classes.grow}/>
                    <AppMenu/>
                    <HeaderMenu/>
                </Toolbar>
            </AppBar>
        </div>
    );
}

export default withStyles(styles)(withRouter(HeaderBar));