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
    componentDidMount: function() {

    },
    submitForm: function(e) {
        e.preventDefault();
        pusher = new Pusher('cea6dff5fc1f38a2d45d');
        var project_id = parseInt($('select[name=project]').val());
        var project = _.where(apps, {id: project_id})[0];
        this.setState({project: project });
        //if (app_data.survey_url !== "") {
        //    window.open(app_data.survey_url, null, 'height=1204, width=680, toolbar=0, location=0, status=1, scrollbars=1, resizable=1');
        //}
        var project_uri = project.resource_uri;
        var app_name = project.name;
        var email = $('input[name=email]').val();
        // creates a deployment app name from the project name and random characters
        var deploy_id = app_name.toLowerCase() + Math.random().toString().substr(2,6);
        deploy_id = deploy_id.replace(/[. -]/g, '');

        //window.Intercom('boot', {
        //        app_id: App.INTERCOM_APP_ID,
        //        email: email,
        //        user_agent_data: navigator.userAgent
        //    }
        //);
        request
            .post('http://127.0.0.1:8000/api/v1/deployments/')
            .send({
                project: project_uri,
                email: email,
                deploy_id: deploy_id
            })
            .end(function(res){
                React.unmountComponentAtNode(document.getElementsByClassName("container")[0]);
                React.render(
                    <DeployerStatusWidget deploy_id={deploy_id} />,
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
                    <EmailAddressInput />
                    <button className="btn btn-success" type="submit">Launch demo site</button>
                </form>
            </div>
        );
    }
});

var DeployerStatusWidget = React.createClass({
    propTypes: {
        deploy_id: React.PropTypes.string
    },
    getInitialState() {
        return {
            statusMessage: "Starting deployment...",
            percent: 5
        }
    },
    componentDidMount() {
        this.channel = App.pusher.subscribe(this.props.deploy_id);
        this.channel.bind('info_update', this.updateInfoStatus);
        this.channel.bind('deployment_complete', this.deploymentSuccess);
        this.channel.bind('deployment_failed', this.deploymentFail);
    },
    render() {
        var style = {
            width: this.state.percent + '%'
        };
        return (
            <div id="central-widget">
                <div className="form-deploy">
                    <img src="/static/img/ajax-loader.gif" alt="loader" className="spinner" />
                    <h3>Deploying</h3>
                    <div className="progress progress-striped active">
                        <div className="progress-bar" role="progressbar" style={style} aria-valuenow={this.state.percent} aria-valuemin="0" aria-valuemax="100">
                            <span className="sr-only">{this.state.percent}% Complete</span>
                        </div>
                    </div>
                    <div className="alert alert-info" id="info-message-section">
                        <span className="glyphicon glyphicon-wrench"></span>
                        <span id="info-message"> {this.state.statusMessage}</span>
                    </div>
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
            value: "",
            state: "VALID",
            error_msg: ""
        }
    },
    validateInput: function (e) {
        var email = e.target.value;
        var re = /\S+@\S+\.\S+/;
        if (email === "" || !re.test(email)) {
            this.setState({value: email, state: "INVALID", error_msg: "You must enter an email address!"});
        }
        else if (email.length > 60) {
            this.setState({
                value: email,
                state: "INVALID",
                error_msg: "You've entered an email address that is too long (>60 characters)"
            });
        }
        else {
            this.setState({
                value: email,
                state: "VALID",
                error_msg: ""
            });
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
                            onChange={this.validateInput}
                            id="email_input"
                            placeholder="name@domain.com"
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
