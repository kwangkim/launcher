var STATIC_URL = window.STATIC_URL;
var request = window.superagent;
var pusher;

/* MAIN VIEW */

var DeployerWidget = React.createClass({
    propTypes: {
        projects: React.PropTypes.array
    },
    getInitialState() {
        return {
            project: {}
        };
    },
    submitForm: function (e) {
        e.preventDefault();
        if (!this.refs.emailInputWidget.validateInput()) {
            return false;
        }

        pusher = new Pusher('cea6dff5fc1f38a2d45d');
        // get project info from array
        var project_id = parseInt($('select[name=project]').val());
        var project = _.where(apps, {id: project_id})[0];
        this.setState({project: project});

        //show survey if it exists
        if (project.survey_form_url !== "") {
            window.open(project.survey_form_url, null, 'height=1204, width=680, toolbar=0, location=0, status=1, scrollbars=1, resizable=1');
        }
        var project_uri = project.resource_uri;
        var app_name = project.name;
        var email = $('input[name=email]').val();
        // creates a deployment app name from the project name and random characters
        var deploy_id = app_name.toLowerCase() + Math.random().toString().substr(2, 6);
        deploy_id = deploy_id.replace(/[. -]/g, '');

        window.Intercom('boot', {
                app_id: App.INTERCOM_APP_ID,
                email: email,
                user_agent_data: navigator.userAgent
            }
        );
        request
            .post('/api/v1/deployments/')
            .send({
                project: project_uri,
                email: email,
                deploy_id: deploy_id
            })
            .end(function (res) {
                var statusComponent;
                if (res.ok) {
                    statusComponent = <DeploymentStatusWidget deployId={deploy_id} appName={app_name} />;
                } else {
                    statusComponent = <DeploymentFailedWidget statusMessage={res.text} />;
                }
                React.unmountComponentAtNode(document.getElementsByClassName("container")[0]);
                React.render(
                    statusComponent,
                    document.getElementsByClassName("container")[0]
                );
            });
    },
    render() {
        return (
            <div id="central-widget">
                <form className="form-deploy" method="post" onSubmit={this.submitForm}>
                    <a href="http://www.appsembler.com" id="appsembler-logo">
                        <img src={STATIC_URL + "img/appsembler_logo.png"} alt="Appsembler logo" />
                    </a>
                    <h3 className="form-deploy-heading">Pick a project:</h3>
                    <ProjectSelectWidget projects={this.props.projects} />
                    <EmailAddressInput ref="emailInputWidget" />
                    <button className="btn btn-success" type="submit">Launch demo site</button>
                </form>
            </div>
        );
    }
});

var DeploymentStatusWidget = React.createClass({
    propTypes: {
        appName: React.PropTypes.string,
        deployId: React.PropTypes.string
    },
    getInitialState() {
        return {
            percent: 5,
            statusMessage: "Starting deployment..."
        }
    },
    componentDidMount() {
        this.channel = pusher.subscribe(this.props.deployId);
        this.channel.bind('info_update', this.updateInfoStatus);
        this.channel.bind('deployment_complete', this.deploymentSuccess);
        this.channel.bind('deployment_failed', this.deploymentFail);
    },
    deploymentFail(data) {
        React.unmountComponentAtNode(document.getElementsByClassName("container")[0]);
        React.render(
            <DeploymentFailedWidget statusMessage={data.message} />,
            document.getElementsByClassName("container")[0]
        );
    },
    deploymentSuccess(data) {
        React.unmountComponentAtNode(document.getElementsByClassName("container")[0]);
        React.render(
            <DeploymentSuccessWidget appInfo={data} />,
            document.getElementsByClassName("container")[0]
        );
    },
    updateInfoStatus(data) {
        this.setState({
            statusMessage: data.message,
            percent: data.percent
        })
    },
    render() {
        return (
            <div id="central-widget">
                <div className="form-deploy">
                    <img src="/static/img/ajax-loader.gif" alt="loader" className="spinner" />
                    <h3>Deploying {this.props.appName}</h3>
                    <ProgressBar percent={this.state.percent} />
                    <div className="alert alert-info" id="info-message-section">
                        <span className="glyphicon glyphicon-wrench"></span>
                        <span id="info-message"> {this.state.statusMessage}</span>
                    </div>
                </div>
            </div>
        )
    }
});

var DeploymentSuccessWidget = React.createClass({
    propTypes: {
        appInfo: React.PropTypes.object,
    },
    render() {
        var hasAuthInfo = this.props.appInfo.username || this.props.appInfo.password;
        return (
            <div id="central-widget">
                <div className="form-deploy">
                    <h3>Deployed {this.props.appInfo.app_name}</h3>
                    <div className="alert alert-success" id="info-message-section">
                        <span className="glyphicon glyphicon-ok"></span>
                        <span id="info-message"> {this.props.appInfo.message}</span>
                    </div>
                    {this.props.appInfo.app_url.split(" ").map(function (url) {
                        return <p>
                            <a className="app-url" href={url}>{url}</a>
                        </p>
                    })}
                    {hasAuthInfo ?
                        <div className="alert alert-info auth-details">Authentication details
                            <br/>
                            <strong>Username:</strong> {this.props.appInfo.username}
                            <br />
                            <strong>Password:</strong> {this.props.appInfo.password}
                        </div>
                        : null}
                </div>
            </div>
        )
    }
});

var DeploymentFailedWidget = React.createClass({
    propTypes: {
        statusMessage: React.PropTypes.string
    },
    render() {
        return (
            <div id="central-widget">
                <div className="form-deploy">
                    <h3>Deployment failed!</h3>
                    <div className="alert alert-danger" id="info-message-section">
                        <span className="glyphicon glyphicon-remove"></span>
                        <span id="info-message"> {this.props.statusMessage}</span>
                    </div>
                </div>
            </div>
        )
    }
});

var ProgressBar = React.createClass({
    propTypes: {
        percent: React.PropTypes.number
    },
    render() {
        var style = {
            width: this.props.percent + '%'
        };
        return (
            <div className="progress progress-striped active">
                <div className="progress-bar" role="progressbar" style={style} aria-valuenow={this.props.percent} aria-valuemin="0" aria-valuemax="100">
                    <span className="sr-only">{this.props.percent}% Complete</span>
                </div>
            </div>
        )
    }
});

var ProjectSelectWidget = React.createClass({
    propTypes: {
        projects: React.PropTypes.array
    },
    render() {
        return (
            <select name="project" id="project_select" className="form-control">
                {this.props.projects.map(function (project) {
                    return <ProjectItem project={project} key={project.id} />;
                })}
            </select>
        );
    }
});

var ProjectItem = React.createClass({
    propTypes: {
        project: React.PropTypes.object
    },
    selectProject(e) {
        console.log(e);
        console.log(this.props.project);
    },
    render() {
        return (
            <option value={this.props.project.id} onChange={this.selectProject}>{this.props.project.name}</option>
        );
    }
});

var ValidationMessage = React.createClass({
    render() {
        return (
            <span className = "help-block" ref="help">{this.props.message}</span>
        );
    }
});

var EmailAddressInput = React.createClass({
    getInitialState() {
        return {
            state: "VALID",
            error_msg: "",
            validated: false
        }
    },
    validateOnChange(e) {
        // only run on change if the validation has been run (and has failed)
        if (this.state.validated) {
            this.validateInput(e);
        }
    },
    validateInput(e) {
        var email = this.refs.emailInput.getDOMNode().value;
        var re = /[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/;
        if (email === "" || !re.test(email)) {
            this.setState({
                state: "INVALID",
                error_msg: "You must enter an email address!",
                validated: true
            });
            return false;
        }
        else if (email.length > 60) {
            this.setState({
                state: "INVALID",
                error_msg: "You've entered an email address that is too long (>60 characters)",
                validated: true
            });
            return false;
        }
        else {
            this.setState({
                state: "VALID",
                error_msg: "",
                validated: true
            });
            return true;
        }
    },
    render() {
        return (
            <div className="email-address-widget">
                <h4>Where can we send the URL</h4>
                <div className="form-group">
                    <div className="input-group">
                        <span className="input-group-addon">
                            <span className="glyphicon glyphicon-envelope"></span>
                        </span>
                        <input
                            type="text"
                            name="email"
                            className="form-control"
                            onChange={this.validateOnChange}
                            id="email_input"
                            placeholder="name@domain.com"
                            ref="emailInput"
                        />
                    </div>
                    <ValidationMessage message={this.state.error_msg} />
                </div>
            </div>
        )
    }
});

React.render(
    <DeployerWidget projects={apps} />,
    document.getElementsByClassName("container")[0]
);
