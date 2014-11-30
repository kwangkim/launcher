var STATIC_URL = window.STATIC_URL;

var DeployerWidget = React.createClass({
    propTypes: {
        projects: React.PropTypes.array
    },
    render: function () {
        return (
            <div id="central-widget">
                <form className="form-deploy" method="post">
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

var ProjectSelectWidget = React.createClass({
    propTypes: {
        projects: React.PropTypes.array
    },
    render: function () {
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
    render: function () {
        return (
            <option value={this.props.project.resource_uri}>{this.props.project.name}</option>
        );
    }
});

var EmailAddressInput = React.createClass({
    getInitialState: function () {
        return {
            value: "",
            state: "VALID",
            error_msg: ""
        }
    },
    validateInput: function(e) {
        var email = e.target.value;
        this.setState({value: email});

        var re = /\S+@\S+\.\S+/;
        var dom = this.refs.help.getDOMNode();
        if(email === "" || !re.test(email)) {
            dom.innerHTML = "You must enter an email address!";
        }
        else if(email.length > 60) {
            dom.innerHTML = "You've entered an email address that is too long (>60 characters)";
        }
        else {
            dom.innerHTML = "";
        }
    },
    render: function () {
        return (
            <div className="email-address-widget">
                <h4>Where can we send the URL</h4>
                <div
                    className = "form-group" >
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
                            ref="dinamo"
                            placeholder="name@domain.com"
                        />
                    </div>
                    < span
                        className = "help-block" ref="help"> </span>
                </div>
            </div>
        )
    }
});

React.render(
    <DeployerWidget projects={apps} />,
    document.getElementsByClassName("container")[0]
);
