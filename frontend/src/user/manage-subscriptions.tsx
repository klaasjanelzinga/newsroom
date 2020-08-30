import * as React from 'react'
import {
    Button,
    createStyles, Paper,
    Table, TableBody,
    TableCell, TableContainer,
    TableHead, TableRow,
    TableSortLabel,
    Typography,
    WithStyles
} from "@material-ui/core";
import {RouteComponentProps, withRouter} from "react-router-dom";
import {withStyles} from "@material-ui/core/styles";
import HeaderBar from "../headerbar/HeaderBar";
import Header from './header'
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import SaveIcon from "@material-ui/icons/Save";
import ArrowRightIcon from "@material-ui/icons/ArrowRight";
import UserProfile from "./UserProfile";
import {InsertLink} from "@material-ui/icons";

const styles = createStyles({
    saveButton: {
        marginRight: '10px',
        marginLeft: '8px',
        fontSize: 13,
    },
    signedInUI: {
        padding: '10px',
        marginLeft: '2px',
    }
});

interface HeadCell {
    disablePadding: boolean;
    id: string;
    label: string;
    numeric: boolean;
}

interface RSSFeed {
    url: string
    description: string
    something: string
}

interface ManageSubscriptionsProps extends RouteComponentProps, WithStyles<typeof styles> {
}

interface MangeSubscriptionsState {
    newRssURL: string
}

class ManageSubscriptions extends React.Component<ManageSubscriptionsProps, MangeSubscriptionsState> {

    userProfile: UserProfile
    state: MangeSubscriptionsState = {
        newRssURL: ""
    }

    constructor(props: ManageSubscriptionsProps) {
        super(props);

        this.userProfile = UserProfile.get()
    }

    checkNewRssURL = (event: unknown): void => {
        console.log("TODO Check RSS URL")
    }


    render() {
        const {classes} = this.props


        const headCells: HeadCell[] = [
            {id: 'name', numeric: false, disablePadding: true, label: 'Dessert (100g serving)'},
            {id: 'calories', numeric: true, disablePadding: false, label: 'Calories'},
            {id: 'fat', numeric: true, disablePadding: false, label: 'Fat (g)'},
            {id: 'carbs', numeric: true, disablePadding: false, label: 'Carbs (g)'},
            {id: 'protein', numeric: true, disablePadding: false, label: 'Protein (g)'},
        ];

        const rssFeeds: RSSFeed[] = [
            {url: "http://www.pitchfork", description: "Music", something: "lskdjfslkdjfsl flakdsj falkdsjf alk jdsfg"},
            {url: "http://www.pitchfork", description: "Music", something: "lskdjfslkdjfsl flakdsj falkdsjf alk jdsfg"},
            {url: "http://www.pitchfork", description: "Music", something: "lskdjfslkdjfsl flakdsj falkdsjf alk jdsfg"},
            {url: "http://www.pitchfork", description: "Music", something: "lskdjfslkdjfsl flakdsj falkdsjf alk jdsfg"},
            {url: "http://www.pitchfork", description: "Music", something: "lskdjfslkdjfsl flakdsj falkdsjf alk jdsfg"},
        ]


        return <div>
            <HeaderBar/>
            <Header title={"Manage subscriptions"}/>

            <div className={classes.signedInUI}>
                <Typography variant="h6" gutterBottom>
                    Welcome {this.userProfile.givenName} {this.userProfile.familyName}!
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                    Subscribe here to news sources. News sources are rss feeds, custom news sources and plugins.
                </Typography>
                <Grid container spacing={3}>
                    <Grid item xs={10}>
                        <TextField
                            required
                            id="url"
                            name="url"
                            label="New RSS-Feed url"
                            fullWidth
                            onChange={(event) => this.setState({newRssURL: event.currentTarget.value})}
                            autoComplete="fname"
                        />

                    </Grid>
                    <Grid item xs={2}>
                        <Button variant="contained" size="small" className={classes.saveButton}
                                onClick={this.checkNewRssURL}>
                            <InsertLink/>
                            Check
                        </Button>
                    </Grid>
                    <Grid item xs={12}>
                        <TableContainer component={Paper}>
                            <Table size="small" aria-label="a dense table">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Dessert (100g serving)</TableCell>
                                        <TableCell align="right">Calories</TableCell>
                                        <TableCell align="right">Fat&nbsp;(g)</TableCell>
                                        <TableCell align="right">Carbs&nbsp;(g)</TableCell>
                                        <TableCell align="right">Protein&nbsp;(g)</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {rssFeeds.map((row) => (
                                        <TableRow key={row.url}>
                                            <TableCell component="th" scope="row">
                                                {row.url}
                                            </TableCell>
                                            <TableCell align="right">{row.description}</TableCell>
                                            <TableCell align="right">{row.something}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Grid>
                </Grid>
                {/*<div className={classes.buttonBar}>*/}
                {/*    <Button variant="contained" size="small" className={classes.saveButton}*/}
                {/*            onClick={this.updateProfile}>*/}
                {/*        <SaveIcon className={classes.saveButton}/>*/}
                {/*        Save*/}
                {/*    </Button>*/}
                {/*    <Button variant="contained" size="small" className={classes.continueButton}*/}
                {/*            onClick={() => {*/}
                {/*                console.log(this.state)*/}
                {/*                this.props.enqueueSnackbar('Profile is acknowledged.', {*/}
                {/*                    variant: 'info',*/}
                {/*                });*/}
                {/*                this.props.history.push('/');*/}
                {/*            }*/}
                {/*            }>*/}
                {/*        <ArrowRightIcon className={classes.saveButton}/>*/}
                {/*        Acknowledge*/}
                {/*    </Button>*/}

                {/*</div>*/}
            </div>


        </div>
    }
}

export default withStyles(styles)(withRouter(ManageSubscriptions));
