# Contributing to Nmstate

:+1: Thank you for contributing! :+1:

The *Nmstate* team is following the guidelines presented in this document.
These are mostly guidelines, not rules. Use your best judgment and follow
these guidelines when contributing to the project.

## Code of Conduct

This project and everyone participating in it is governed by the
[Nmstate Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.
Please report unacceptable behavior to the nmstate team.

## Code structure

The repository is structured as follows:

- `./automation/` - Contains the [automation enviroment](./automation/README.md), 
serving the tests of Nmstate.

- `./doc/` - Contains the documentation. 

- `./examples/` - Contains YAML examples for different configurations.

- `./logo` Logos used for publication.

- `./k8s` k8s folder holds the scripts for kubernetes-nmstate CI.

- `./rust/src/clib` C bindings of nmstate.

- `./rust/src/go/nmstate` Go library of nmstate wrapping the C bindings.
 
- `rust/src/python` Python library of nmstate wrapping the C bindings.
 
- `./rust/src/lib/nispor/` Contains the code related to querying the network state with via Nispor. 

- `./rust/src/lib/nm/` Contains the code related to applying the settings via NetworkManager backend.

- `./rust/src/lib/ovsdb/` Contains the code related to ovsdb communication and structures. 

- `./rust/src/cli/` - Contains command lines tools.

- `./packaging/` - Contains packaging utilities.

- `./tests/` - Contains tests for unit and integration tests.

## Configuring Git

Before starting to contribute, make sure you have the basic git configuration: 
Your name and email. This will be useful when signing your contributions. The 
following commands will set your global name and email, although you can 
change it later for every repo:

```
git config --global user.name "Jane Doe"
git config --global user.email janedoe@example.com`
```

The git editor is your system's default. If you feel more comfortable with a 
different editor for writing your commits (such as Vim), change it with:

```
git config --global core.editor vim
```

If you want to check your settings, use `git config --list` to see all the 
settings Git can find. 

You can refer to [Pro Git](https://git-scm.com/book/en/v2) for further information.


## How to Contribute

- Bugs: Tracked as ([GitHub issues](https://github.com/nmstate/nmstate/issues)).
- Enhancements: RFE suggestions are tracked as
([GitHub issues](https://github.com/nmstate/nmstate/issues)).
- Code: Managed on [GitHub](https://github.com/nmstate/nmstate) through
  Pull Requests ([PR](https://github.com/nmstate/nmstate/pulls)).

Please check the [developer guide](https://www.nmstate.io/devel/dev_guide.html).

#### Pull Requests
Please follow these steps to have your contribution considered by the maintainers:

1. Run and pass the unit tests and integration tests locally. In order to do
this, please follow the steps in the [run-test.sh documentation](automation/README.md).
2. Follow the instructions on
[how to open a PR](https://opensource.guide/how-to-contribute/#opening-a-pull-request).
3. Follow the [Coding and Style Guidelines](#Coding-and-Style-Guidelines).
4. After you submit your pull request, verify that all
[status checks](https://help.github.com/articles/about-status-checks/) are passing.

### Write a good commit message
Here are a few rules to keep in mind while writing a commit message

   1. Separate subject from body with a blank line
   2. Limit the subject line to 50 characters
   3. Capitalize the subject line
   4. Do not end the subject line with a period
   5. Use the imperative mood in the subject line
   6. Wrap the body at 72 characters
   7. Use the body to explain what and why vs. how

 A good commit message looks something like this
```
  Summarize changes in around 50 characters or less

 More detailed explanatory text, if necessary. Wrap it to about 72 characters 
 or so. In some contexts, the first line is treated as the subject of the 
 commit and the rest of the text as the body. The blank line separating the 
 summary from the body is critical (unless you omit the body entirely); various 
 tools like `log`, `shortlog` and `rebase` can get confused if you run the two 
 together.

 Explain the problem that this commit is solving. Focus on why you are making 
 this change as opposed to how (the code explains that).
 Are there side effects or other unintuitive consequences of this change? 
 Here's the place to explain them.

 Further paragraphs come after blank lines.

  - Bullet points are okay, too

  - Typically a hyphen or asterisk is used for the bullet, preceded by a single 
    space, with blank lines in between, but conventions vary here

 If you use an issue tracker, put references to them at the bottom, like this:

 Resolves: #123
 See also: #456, #789

Do not forget to sign your commit! Use `git commit -s`

```

This is taken from [chris beams git commit](https://chris.beams.io/posts/git-commit/).
You may want to read this for a more detailed explanation (and links to other 
posts on how to write a good commit message). This content is licensed under 
[CC-BY-SA](https://creativecommons.org/licenses/by-sa/4.0/).

## Coding and Style Guidelines

- Nmstate is written primarily in Python, and its coding style should follow
  the best practices of Python coding unless otherwise declared.
- Nmstate uses the [black](https://github.com/python/black) code formatter
- PEP8 is holy.
- Tests are holy.
  Production code must be covered by unit tests and/or basic integration tests.
  When too many mocks are required, it is often a smell that the tested code
  is not well structured or in some cases a candidate for integration tests.
- Packages, modules, functions, methods and variables should use
  underscore_separated_names.
- Class names are in CamelCase.
- Imports should be grouped in the following order:
  - Standard library imports
  - Related third party imports
  - Local application-specific or library-specific imports.
- All indentation is made of the space characters.
  Tabs must be avoided. In makefiles, however, tabs are obligatory.
  White space between code stanzas are welcome. They help to create breathing
  while reading long code.
  However, splitting stanzas into helper functions could be even better.

Ref:
https://www.ovirt.org/develop/developer-guide/vdsm/coding-guidelines/

### Clean Code
Do your best to follow the clean code guidelines.

- Name classes using a noun.
- Name functions/methods using a verb.
- Make them as small as possible.
- They should do one thing only and do it well.
  One thing means one level of abstraction.
  The names and code should reflect that.
- Methods/functions should be organized per level of abstraction,
  where callee sits below their caller.
- Avoid output-arguments (arguments to output data out of a function/method).
- Don’t use boolean arguments, use 2 functions/methods instead.
- Don’t return an error code, throw an exception instead.

Ref: Book: Clean Code by Robert C. Martin (Uncle Bob)

## Installing and Compiling
This guide will walk you through the process of installing and compiling nmstate from the source. For installing stable release or other installation methods, please refer to nmstate installation guide: https://nmstate.io/user/install.md

### Prerequisite 
A Linux operating system is required. For Windows or macOS users, you can set up a Linux environment using VirtualBox, VMware, or Virt-manager.

### Install Cargo Tool
Cargo is Rust's build system and package manager, necessary for working with Rust programs, such as Nmstate.
```
- sudo apt update && sudo apt install cargo git # Debian/Ubuntu
- sudo dnf install cargo git # Fedora
- sudo yum install cargo git # RHEL
```

### Get the Source Code
Clone the Nmstate repository: 
```
- git clone https://github.com/nmstate/nmstate.git
- cd nmstate
```

### Compilation
Run the following command at the top level of the code to compile the project:
```
- make
```

### Running the Compiled Program
After successful compilation, you can run the nmstatectl tool to display the current network state:
```
- target/debug/nmstatectl show # To dump the state in json format, use the ‘--json’ flag.
``` 

For the complete developer’s guide, head over to our full documentation: https://nmstate.io/devel/dev_guide.html 
