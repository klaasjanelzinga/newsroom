import { withStyles } from '@material-ui/core';
import { withSnackbar } from 'notistack';
import PropTypes from 'prop-types';
import React from 'react';
import { withRouter } from 'react-router-dom';
import HeaderBar from '../headerbar/HeaderBar';
import UserProfile from './UserProfile';

const styles = {
    
};

class SignOut extends React.Component {

    notifySuccesfulUpdate() {
        this.props.enqueueSnackbar('You were signed out.', {
            variant: 'info',
        });
    }


    componentWillMount() {
        UserProfile.delete();
        this.notifySuccesfulUpdate();
        this.props.history.push('/');
    }

    render() {
        return <div>
            <HeaderBar />
            Signing out!
        </div>
    }
}

SignOut.propTypes = {
    classes: PropTypes.object.isRequired,
  };
  
  export default withStyles(styles)(withRouter(withSnackbar(SignOut)));
  
  