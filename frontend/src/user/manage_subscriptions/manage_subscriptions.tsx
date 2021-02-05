import * as React from 'react'
import {
    createStyles,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
    WithStyles
} from "@material-ui/core";
import {RouteComponentProps, withRouter} from "react-router-dom";
import {withStyles} from "@material-ui/core/styles";
import HeaderBar from "../../headerbar/HeaderBar";
import Header from '../header'
import Grid from "@material-ui/core/Grid";
import {Api} from "../../Api";
import {withSnackbar, WithSnackbarProps} from "notistack";
import NewRssFeed from './new_rss_feed';
import ImageAndTitle from "./feed_image_and_title";
import {GetFeedsResponse} from "../model";
import SubscribeUnsubscribeButton from "./subscribe_unsubscribe_button";
import LinearProgress from "@material-ui/core/LinearProgress";
import {withAuthHandling, WithAuthHandling} from "../../WithAuthHandling";


const styles = createStyles({
    signedInUI: {
        padding: '10px',
        marginLeft: '2px',
    },
    subscriptionsTable: {
        marginTop: "30px",
    },
    manageSubscriptions: {
        overflow: "hidden",
    }
});

interface ManageSubscriptionsProps extends WithAuthHandling, WithSnackbarProps, RouteComponentProps, WithStyles<typeof styles> {
}

interface SubscribeResponse {
    email: string;
}

interface MangeSubscriptionsState {
    feedsForUser: GetFeedsResponse[];
    isLoading: boolean
}

class ManageSubscriptions extends React.Component<ManageSubscriptionsProps, MangeSubscriptionsState> {

    api: Api
    state: MangeSubscriptionsState = {
        feedsForUser: [],
        isLoading: false,
    }

    constructor(props: ManageSubscriptionsProps) {
        super(props);

        this.api = new Api(props)
    }


    componentDidMount() {
        this.fetchAvailableFeeds()
    }

    fetchAvailableFeeds() {
        this.setState({isLoading: true})
        this.api.get<[GetFeedsResponse]>("/feeds")
            .then(feedsWithInfo => {
                this.setState({feedsForUser: feedsWithInfo[1]})
            })
            .catch((reason: Error) => console.error(reason))
            .finally(() => this.setState({isLoading: false}))
    }

    showNotification(message: string) {
        this.props.enqueueSnackbar(message, {
            variant: "info"
        })
    }

    subscribeTo(feedForUser: GetFeedsResponse) {
        this.api.post<SubscribeResponse>(`/feeds/${feedForUser.feed.feed_id}/subscribe`)
            .then(() => {
                this.showNotification('Subscribed')
                this.setState({
                    feedsForUser: this.state.feedsForUser.map(feed => {
                        if (feed.feed.feed_id === feedForUser.feed.feed_id) {
                            feed.user_is_subscribed = true
                        }
                        return feed
                    })
                })
            })
            .catch((reason:Error) => console.error(reason))
    }

    unsubscribeFrom(feedForUser: GetFeedsResponse) {
        this.api.post<SubscribeResponse>(`/feeds/${feedForUser.feed.feed_id}/unsubscribe`)
            .then(() => {
                this.showNotification('Unsubscribed')
                this.setState({
                    feedsForUser: this.state.feedsForUser.map(feed => {
                        if (feed.feed.feed_id === feedForUser.feed.feed_id) {
                            feed.user_is_subscribed = false
                        }
                        return feed
                    })
                })
            })
            .catch(reason => console.error(reason))
    }

    render() {
        const {classes} = this.props


        return <div className={classes.manageSubscriptions}>
            <HeaderBar/>
            <Header title={"Manage subscriptions"}/>

            <div className={classes.signedInUI}>
                <Typography variant="h6" gutterBottom>
                    Welcome!
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                    Subscribe here to news sources. News sources are rss feeds, custom news sources or plugins.
                </Typography>
                <NewRssFeed subscribe_callback={(feedResponse: GetFeedsResponse) => this.subscribeTo(feedResponse)}
                            unsubscribe_callback={(feedResponse: GetFeedsResponse) => this.unsubscribeFrom(feedResponse)}/>

                <div className={classes.subscriptionsTable}>

                    <Typography variant="body2" gutterBottom>
                        Or manage your subscriptions:
                    </Typography>
                    {this.state.isLoading &&  <LinearProgress />}
                    <Grid container spacing={3}>
                        <Grid item xs={12}>
                            <TableContainer component={Paper}>
                                <Table size="small" aria-label="a dense table">
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Subscribe / Unsubscribe</TableCell>
                                            <TableCell>Title</TableCell>
                                            <TableCell>Description</TableCell>
                                            <TableCell>URL</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {this.state.feedsForUser.map((feedForUser) => (
                                            <TableRow key={feedForUser.feed.feed_id}>
                                                <TableCell>
                                                    <SubscribeUnsubscribeButton feedResponse={feedForUser}
                                                                                subscribe_callback={feedResponse => this.subscribeTo(feedResponse)}
                                                                                unsubscribe_callback={feedResponse => this.unsubscribeFrom(feedResponse)}/>
                                                </TableCell>
                                                <TableCell component="th" scope="row">
                                                    <ImageAndTitle feed={feedForUser.feed}/>
                                                </TableCell>
                                                <TableCell>{feedForUser.feed.description}</TableCell>
                                                <TableCell>{feedForUser.feed.url}</TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </Grid>
                    </Grid>
                </div>
            </div>
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(ManageSubscriptions))))
