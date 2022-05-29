import { Radio, Spin } from 'antd';
import axios from 'axios';
import { useState } from 'react';
import styled from "styled-components";


const StyledPanel = styled.div`
    width: 350px;
    padding: 10px;
    background-color: white;
    border-radius: 12px;
    border-style: dashed;
    border: 2px solid #0279C1;
    margin-left: 20px;
`;

const StyledButton = styled.div`
    margin: 0 auto;
    margin-top: 10px;
    padding: 10px;
    font-size: 18px;
    color: white;
    font-weight: bold;
    background-color: #000000;
    cursor : pointer;
    border-radius: 10px;
`;

const StyledPerson = styled.div`
    padding: 10px;
    margin: 5px;
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: bold;
`;


function PeoplePanel(props) {
    const [value, setValue] = useState('');
    const [timeline, setTimeline] = useState();
    const [id, setId] = useState();

    const onChange = (e) => {
        console.log('Selected Person:', e.target.value);
        setValue(e.target.value);
      };

    const rendering = (people) => {
        console.log(props)
        const people_imgs = [];
        for (var prop in people) {
            people_imgs.push(
                <StyledPerson key={prop}>
                    <img src={`data:image/jpeg;base64,${people[prop]}`} 
                        width="80px"
                        style={{borderRadius: "35px"}} />
                    <div style={{flexGrow: "1"}}>
                        <div>{prop}</div>
                    </div>
                </StyledPerson>);
        }
        return people_imgs;
    };


    const radioButton = (people) => {
        const buttons = [];

        for (var prop in people) {
            buttons.push(
                <Radio key={prop} value={prop} />
            );
        }

        return (
            <Radio.Group onChange={onChange} value={value} 
                style={{display: "flex", flexDirection: "column", justifyContent: "space-around"}}>
                {buttons}
            </Radio.Group>
        );
    };

    

    const personSelect = async(e) => {
        e.preventDefault();

        // console.log(e.target)
        // const formData = new FormData();
        const URL = "http://101.101.218.23:30001/timeline-face";

        // formData.append('person', value);
        // formData.append('id', props.id);

        // console.log(formData)

        await axios.post(URL, {"face":value, "id":props.id}
        ).then((response)=> {
            console.log(response)
            setId(response.data.id)
            setTimeline(response.data.timeline)
        }).catch((error) => {
            console.log("Failure :(")
        })

    };

    return (
        <StyledPanel>
            <div style={{display: "flex", alignItems: "stretch"}}>
                <div style={{flexGrow: "1"}}>{rendering(props.people)}</div>
                <div style={{display: "flex", paddingRight: "10px", alignItems: "stretch"}}>
                    {radioButton(props.people)}
                </div>
            </div>
                <StyledButton onClick={personSelect}>
                        인물 선택 완료!
                </StyledButton>

            
        </StyledPanel>
    );
}

export default PeoplePanel;
