import * as React from 'react'
import {withSnackbar, WithSnackbarProps} from "notistack";
import {Api} from "../../Api";
import {RouteComponentProps, withRouter} from "react-router-dom";
import {Button, createStyles, Theme, WithStyles, withStyles} from "@material-ui/core";
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import {InsertLink} from "@material-ui/icons";
import {GetFeedsResponse} from "../model";
import ImageAndTitle from "./feed_image_and_title"
import SubscribeUnsubscribeButton from "./subscribe_unsubscribe_button";

interface NewRssFeedState {
    newURL: string;
    foundFeed: GetFeedsResponse | null;
}

interface NewRssFeedProps extends RouteComponentProps, WithSnackbarProps, WithStyles<typeof styles> {
    subscribe_callback: (feed: GetFeedsResponse) => void
    unsubscribe_callback: (feed: GetFeedsResponse) => void
}

const styles = (theme: Theme) => createStyles({
    button: {
        marginRight: '10px',
        marginLeft: '8px',
        fontSize: 13,
    },
    foundPanel: {
        padding: "10px",
        backgroundColor: "lightgray",
    },
    foundPanelItem: {
        padding: "3px",
    },
    subscribeButton: {
        marginTop: "10px",
    },
});


class NewRssFeed extends React.Component<NewRssFeedProps, NewRssFeedState> {

    api: Api
    state: NewRssFeedState = {
        newURL: "",
        foundFeed: null,
    }

    constructor(props: NewRssFeedProps) {
        super(props);

        this.api = new Api(props)
    }

    checkNewRssURL = (event: unknown): void => {
        this.api.post<GetFeedsResponse>(`/feeds/for_url?url=${this.state.newURL}`)
            .then(for_url_response => {
                this.setState({foundFeed: for_url_response[1]})
            })
            .catch(reason => console.error(reason))
    }

    isValidURL(url: string): boolean {
        const is_https = url.startsWith("http")
        const is_not_null = url !== ""

        return is_https && is_not_null
    }

    subscribeTo(feedResponse: GetFeedsResponse | null) {
        if (feedResponse) {
            this.props.subscribe_callback(feedResponse)
            this.setState({
                foundFeed: {
                    feed: feedResponse.feed,
                    user_is_subscribed: true
                }
            })
        }
    }

    unsubscribeFrom(feedResponse: GetFeedsResponse | null) {
        if (feedResponse) {
            this.props.unsubscribe_callback(feedResponse)
            this.setState({
                foundFeed: {
                    feed: feedResponse.feed,
                    user_is_subscribed: false
                }
            })
        }
    }


    render() {
        const {classes} = this.props
        return <Grid container>
            <Grid container>
                <Grid item xs={10}>
                    <TextField
                        required
                        id="url"
                        name="url"
                        label="Add new RSS-Feed url here and click CHECK URL"
                        fullWidth
                        onChange={(event) => this.setState({newURL: event.currentTarget.value})}
                        autoComplete="fname"
                    />
                </Grid>
                <Grid item xs={2}>
                    <Button variant="contained"
                            size="small"
                            disabled={this.isValidURL(this.state.newURL) !== true}
                            className={classes.button}
                            onClick={this.checkNewRssURL}>
                        <InsertLink/>
                        Check url
                    </Button>
                </Grid>
            </Grid>
            {this.state.foundFeed && <Grid container className={classes.foundPanel}>

                <Grid item xs={2} className={classes.foundPanelItem}>URL</Grid>
                <Grid item xs={10} className={classes.foundPanelItem}>{this.state.foundFeed.feed.url}</Grid>
                <Grid item xs={2} className={classes.foundPanelItem}>Title</Grid>
                <Grid item xs={10} className={classes.foundPanelItem}>
                    <ImageAndTitle feed={this.state.foundFeed.feed} />
                </Grid>
                <Grid item xs={2} className={classes.foundPanelItem}>Description</Grid>
                <Grid item xs={10} className={classes.foundPanelItem}>{this.state.foundFeed.feed.description}</Grid>
                <Grid item xs={2} className={classes.foundPanelItem}>
                    <SubscribeUnsubscribeButton feedResponse={this.state.foundFeed}
                                                subscribe_callback={feedResponse => this.subscribeTo(feedResponse)}
                                                unsubscribe_callback={feedResponse => this.unsubscribeFrom(feedResponse)} />
                </Grid>
            </Grid>}
        </Grid>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(NewRssFeed)));