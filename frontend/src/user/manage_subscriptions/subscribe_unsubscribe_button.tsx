import * as React from "react";
import {Button, createStyles, withStyles, WithStyles} from "@material-ui/core";
import {GetFeedsResponse} from "../model";
import SubscriptionsIcon from "@material-ui/icons/Subscriptions";
import UnsubscribeIcon from "@material-ui/icons/Unsubscribe";

const styles = createStyles({
    button: {
        marginRight: '10px',
        marginLeft: '8px',
        fontSize: 13,
    },
})

interface SubscribeUnsubscribeButtonProps extends WithStyles<typeof styles> {
    feedResponse: GetFeedsResponse;
    subscribe_callback: (feed: GetFeedsResponse) => void;
    unsubscribe_callback: (feed: GetFeedsResponse) => void;
}


const SubscribeUnsubscribeButton: React.FunctionComponent<SubscribeUnsubscribeButtonProps> = (props: SubscribeUnsubscribeButtonProps) => {
    const {classes} = props

    if (props.feedResponse.user_is_subscribed) {
        return <Button size="small"
                       onClick={(): void => props.unsubscribe_callback(props.feedResponse)}
                       className={classes.button}>
            <UnsubscribeIcon/>
            Unsubscribe
        </Button>
    }
    return <Button size="small"
                   onClick={(): void => props.subscribe_callback(props.feedResponse)}
                   className={classes.button}>
        <SubscriptionsIcon/>
        Subscribe
    </Button>
}

    export default withStyles(styles)(SubscribeUnsubscribeButton)