import sqlite3
import random
import re
import sys
from tabulate import tabulate
from datetime import datetime, timedelta, date, time
from time import sleep

sqlConnection = sqlite3.connect('Walk-In-Clinic-DB.db')
cursor = sqlConnection.cursor()
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,3}\b'
symptoms = r'\b^[a-zA-Z]+[a-zA-Z-_ ]*[a-zA-Z]$\b'
currentDate = datetime.now().date()
phone_number = "^\d{10}$"
n = 1
Password_Attempt = 0
Allow_Attempts = 3
mydata = []


class PatientModule:
    def __init__(self):
        self.existing_email = "",
        self.oldpatientnumber = 0

    def patientRegistration(self):

        firstName = input("\n Please Enter First Name to Register :").upper()
        bool_first_name = firstName.isalpha()
        while not bool_first_name:
            firstName = input("\n Please Enter valid First Name :").upper()
            bool_first_name = firstName.isalpha()

        lastName = input("\n Please Enter Last Name to Register :").upper()
        bool_last_name = lastName.isalpha()
        while not bool_last_name:
            lastName = input("\n Please Enter Valid Last Name :").upper()
            bool_last_name = lastName.isalpha()

        GenderValidation = True
        Gender = ""
        while GenderValidation:
            Gender = input("\n Please Enter your gender(M/F):").upper()
            if Gender == '' or not Gender in ('M', 'F'):
                print('\n\t Please answer with M or F!')
            else:
                GenderValidation = False

        # Validate DOB in dd/mm/yyyy format and should be greater than currentDate.
        isValidDate = True
        bdate = date
        while isValidDate:
            try:
                birthday = input("\n Please Enter date of birth in 'dd/mm/yyyy' format : ")
                day, month, year = birthday.split('/')
                date(int(year), int(month), int(day))

                bdate = datetime.strptime(birthday, '%d/%m/%Y').date()
                if bdate > currentDate:
                    print("\n\t Birth Date can not be greater than today's date")
                    continue
                else:
                    pass
            except ValueError:
                continue
            isValidDate = False

        emailId = input("\n Please Enter Email Address to Register :")
        emailId_Val = bool(re.fullmatch(email_regex, emailId))
        while not emailId_Val:
            emailId = input("\n Please Enter Valid Email Address to Register :")
            emailId_Val = re.fullmatch(email_regex, emailId)

        contactnumber = input("\n Please Enter Ten Digit Contact Number:")
        Pattern = bool(re.match(phone_number, contactnumber))
        contact_is_match = bool(Pattern)
        while not contact_is_match:
            contactnumber = ""
            contactnumber = input("\n Please Enter the valid Ten Digit Contact Number:")
            contact_is_match = bool(re.match(phone_number, contactnumber))

        # Insert all the data into table
        cursor.execute("SELECT count(PatientID) FROM PatientData where [EmailID]=? ; ", [emailId])
        result = cursor.fetchone()
        if result[0] >= 1:
            print("\n User already exits ! PLease Login.")
        else:
            cursor.execute("""INSERT INTO PatientData(FirstName,LastName,Gender,DOB,[EmailID],[PhoneNumber]) VALUES (?,?,?,?,?,?) """,
                           (firstName, lastName, Gender, bdate, emailId, contactnumber))
            sqlConnection.commit()

            cursor.execute("SELECT PatientID FROM PatientData where [EmailID]=?; ", [emailId])
            recordspatientid = cursor.fetchone()[0]
            recordspatientnumber = 1000 + recordspatientid
            input_data = (recordspatientnumber, recordspatientid)
            cursor.execute('''UPDATE PatientData SET PatientNumber = ?  WHERE [PatientID]=? ''', input_data)
            sqlConnection.commit()

            cursor.execute("SELECT PatientNumber FROM PatientData where [EmailID]=? ; ", [emailId])
            patientNumber = cursor.fetchone()
            print(
                '-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print(
                ' \n\t Hi ' + firstName + ' ' + lastName + ', \n\n\t your profile is created successfully for EmailID : ' + emailId + ', and Your Patient Number '
                                                                                                                                      'is : '
                + str(patientNumber[0]) + '.\n\n\t Please login using your above specified EmailID and assigned Patient Number to request an appointment.!')
            print(
                '-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            self.audit(recordspatientnumber)

    def patientLogin(self):
        self.existing_email = input("\n Please Enter Email Address to login :")
        bool_existing_email = bool(re.fullmatch(email_regex, self.existing_email))
        while not bool_existing_email:
            self.existing_email = input("\n Please Enter Valid Email Address to login :")
            bool_existing_email = re.fullmatch(email_regex, self.existing_email)

        error_patientnumber = True
        while error_patientnumber:
            try:
                self.oldpatientnumber = int(input("\n Please enter assigned patient number to login :").upper())
            except ValueError:
                continue
            error_patientnumber = False

        cursor.execute("SELECT count(PatientNumber) FROM PatientData where [EmailID]=? and [PatientNumber]=?; ", [self.existing_email, self.oldpatientnumber])
        olduserresult = cursor.fetchone()
        if olduserresult[0] >= 1:
            cursor.execute("SELECT FirstName,LastName FROM PatientData where [EmailID]=? and [PatientNumber]=?; ", [self.existing_email, self.oldpatientnumber])
            fname, lname = cursor.fetchone()

            print("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            print("\n\t Hello," + fname + ' ' + lname)
            print("\t Welcome To The Medical Care Centre.")

            self.requestUserInput(self.existing_email, self.oldpatientnumber)
        else:
            cursor.execute("SELECT count(PatientId) FROM PatientData where [EmailID]=? ; ", [self.existing_email])
            existinguser_result = cursor.fetchone()
            if existinguser_result[0] == 1:
                print("\n\t Incorrect Patient Number!")
            else:
                print("\n Patient Account Does not Exists!Please register.")

    def requestUserInput(self, existing_email, oldpatientnumber):

        currentdate = datetime.today().strftime('%d/%m/%Y')
        print("\n------------------------------------------------")
        print("Please select below options :")
        print("------------------------------------------------")
        error_input_num_ASK = True
        while error_input_num_ASK:

            try:
                input_value_ASK = int(
                    input(
                        'Enter   1 To Request An Appointment \n\t\t2 To Confirm the appointment \n\t\t3 To View the scheduled details\n\t\t4 To View the '
                        'Prescriptions\n\t\t5 To View the cancelled appointment details\n'))
            except ValueError:
                continue
            else:
                error_input_num_ASK = False
                if input_value_ASK < 1 or input_value_ASK >= 7:
                    print("invalid input.{}".format(input_value_ASK))
                else:
                    # --------------------------------To Request An Appointment ---------------------------------
                    if input_value_ASK == 1:
                        cursor.execute('select count(*) as cnt from  PatientAppointment where PatientNumber=? and ScheduledDate=?',
                                       [self.oldpatientnumber, currentDate])
                        logincnts = cursor.fetchone()[0]

                        #### Only Three Appontment Slots per day
                        if logincnts < 3:

                            patientsymptoms_primary = input("\n Please enter the Primary Symptoms:")
                            bool_patientsymptoms_primary = bool(re.fullmatch(symptoms, patientsymptoms_primary))
                            while not bool_patientsymptoms_primary:
                                valpatientsymptoms_primary = input("\n Please enter the valid Primary Symptoms with no special symbols and numbers:")
                                bool_patientsymptoms_primary = re.fullmatch(symptoms, valpatientsymptoms_primary)

                            patientsymptoms_other = input("\n Please enter other Symptoms:")
                            bool_patientsymptoms_other = bool(re.fullmatch(symptoms, patientsymptoms_other))
                            while not bool_patientsymptoms_other:
                                Valpatientsymptoms_other = input("\n Please enter any other Symptoms with no special symbols and numbers:")
                                bool_patientsymptoms_other = re.fullmatch(symptoms, Valpatientsymptoms_other)

                            # Validating Primary and Secondary symptoms can not be same.
                            if patientsymptoms_primary == patientsymptoms_other:
                                print('\t Both Primary and secondary symptoms can not be same.')
                            else:
                                cursor.execute("SELECT AccessCount FROM PatientData where [EmailID]=? and [PatientNumber]=?; ",
                                               [existing_email, oldpatientnumber])
                                records = cursor.fetchone()[0]
                                recordcnt = records + 1
                                input_data = (recordcnt,existing_email, oldpatientnumber)
                                cursor.execute('''UPDATE PatientData SET AccessCount = ?  WHERE 
                                                                                        [EmailID]=? and [PatientNumber]=? ''', input_data)
                                sqlConnection.commit()

                                cursor.execute("""INSERT INTO PatientAppointment(PatientNumber,PrimarySymptoms,OtherSymptoms) VALUES (?,?,?) """,
                                               (oldpatientnumber, patientsymptoms_primary, patientsymptoms_other))
                                sqlConnection.commit()
                                print("\n Appointment is requested successfully..! please view the scheduled details after some time.")


                        else:
                            print(' \n You have raised maximum {} appointment requests for the day.'.format(logincnts))

                    # -------------------------------- To Confirm the appointment ---------------------------------
                    # Data-set ScheduledAppointmentFlag=1
                    if input_value_ASK == 2:
                        cursor.execute("SELECT ScheduledDate FROM PatientAppointment as his inner join PatientData as pat on his.PatientNumber=pat.PatientNumber "
                                       "where ScheduledAppointmentFlag=1 and pat.[PatientNumber]=? and his.ConfirmedFlag=0 and PrimarySymptoms is not 'NA' AND "
                                       "OtherSymptoms is not 'NA' "
                                       "and ScheduledDate is not null order by ScheduledDate ASC", [self.oldpatientnumber])
                        ScheduledDate = cursor.fetchall()

                        unique = set(ScheduledDate)
                        if len(unique) == 0:
                            print("\n No appointments scheduled to confirm.")
                        else:
                            cursor.execute(
                                "SELECT his.[AppointmentID],pat.PatientNumber,DoctorName,ScheduledDate,ScheduledTime,CASE WHEN CAST(ScheduledTime as int) >=12 THEN "
                                "'PM'  WHEN CAST(ScheduledTime as int) < 12  THEN 'AM' END as Timezone FROM PatientAppointment as his inner join PatientData as pat on "
                                "his.PatientNumber=pat.PatientNumber where ScheduledAppointmentFlag=1 and his.ConfirmedFlag=0 and pat.[PatientNumber]=? and  "
                                "ScheduledDate >=?",
                                [self.oldpatientnumber, currentdate])
                            confirmcurrentrecords = cursor.fetchall()
                            AppointmentIDs = []
                            if len(confirmcurrentrecords) >= 1:
                                print("\n\t Please confirm your appointment from below details.")
                                print("-----------------------------------------------------------------------------------------------------------------")
                                for confirmcurrentrecord in confirmcurrentrecords:
                                    AppointmentIDs.append(confirmcurrentrecord[0])
                                    print('\tAppointment-ID:' + str(confirmcurrentrecord[0]) + '\t'
                                                                                               '\tPatient-Number:' + str(confirmcurrentrecord[1]) + '\t'
                                                                                                                                                    '\t Doctor-Name:' + str(
                                        confirmcurrentrecord[2]) + '\t'
                                                                   '\t  Date:' + str(confirmcurrentrecord[3]) + '\t'
                                                                                                                '\t  Time:' + str(confirmcurrentrecord[4]) + ' ' + str(
                                        confirmcurrentrecord[5]))

                                error_confirmed = True
                                Validate_confirmedappointmentid = True
                                Validate_cancelledappointmentid = True
                                while error_confirmed:
                                    confirmed_flag = str(input("\n Do you want to confirm the appointment :").upper())
                                    if confirmed_flag == '' or not confirmed_flag in ('YES', 'NO'):
                                        print('\n\t Please answer with yes or no!')
                                    else:
                                        error_confirmed = False
                                        if confirmed_flag == "YES":
                                            confirm_appointment_id = 0

                                            while Validate_confirmedappointmentid:
                                                try:
                                                    confirm_appointment_id = int(input("\n Please enter the Appointment-ID to confirm the appointment:"))
                                                    if confirm_appointment_id not in AppointmentIDs:
                                                        print("\n\t Enter the appointment-id from above specified details.")
                                                        continue
                                                    else:
                                                        break
                                                except ValueError:
                                                    continue

                                            Validate_confirmedappointmentid = False
                                            cursor.execute('update PatientAppointment set ConfirmedFlag=1  where [PatientNumber]=? and [AppointmentID]=?',
                                                           [self.oldpatientnumber, confirm_appointment_id])
                                            sqlConnection.commit()
                                            print('\n Appointment is confirmed.Clinic Management will assist with next steps.')


                                        elif confirmed_flag == "NO":
                                            cancel_appointment_id = 0
                                            while Validate_cancelledappointmentid:
                                                try:
                                                    cancel_appointment_id = int(input("\n Please enter the Appointment-ID to request for cancellation:"))
                                                    if cancel_appointment_id not in AppointmentIDs:
                                                        print("\n\t Enter the appointment-id from above specified details.")
                                                        continue
                                                    else:
                                                        break
                                                except ValueError:
                                                    continue
                                            Validate_cancelledappointmentid = False
                                            cursor.execute(
                                                'update PatientAppointment set ConfirmedFlag=2  where [PatientNumber]=? and [AppointmentID]=? and ConfirmedFlag=0',
                                                [self.oldpatientnumber, cancel_appointment_id])
                                            sqlConnection.commit()
                                            print('\n Your Appointment will be cancelled by the staff member.')
                            else:
                                print("\n No appointments available to confirm.")

                    # ----------------------------------------------------------------- To View the scheduled details ---------------------------------
                    if input_value_ASK == 3:
                        cursor.execute("SELECT ScheduledDate FROM PatientAppointment as his inner join PatientData as pat on his.PatientNumber=pat.PatientNumber "
                                       "where ScheduledAppointmentFlag=1 and pat.[PatientNumber]=? and PrimarySymptoms is not 'NA' AND OtherSymptoms is not 'NA' "
                                       "and ScheduledDate is not null and his.ConfirmedFlag=1 order by ScheduledDate ASC", [self.oldpatientnumber])
                        ScheduledDate = cursor.fetchall()
                        unique = set(ScheduledDate)
                        if len(unique) == 0:
                            print("\n No appointments scheduled.")
                        else:
                            viewpastrecordslist = []
                            viewcurrentrecordslist = []
                            for singledate in unique:
                                stringdate = ''.join(singledate)
                                ViewScheduledDate = datetime.strptime(stringdate, '%Y-%m-%d').date()
                                if ViewScheduledDate < currentDate:
                                    cursor.execute("SELECT his.[AppointmentID],pat.PatientNumber,DoctorName,ScheduledDate,ScheduledTime,CASE WHEN CAST(ScheduledTime as "
                                        "int) >=12 THEN 'PM'  WHEN CAST(ScheduledTime as int) < 12  THEN 'AM' END as Timezone FROM PatientAppointment as his "
                                        "inner join PatientData as pat on his.PatientNumber=pat.PatientNumber where ScheduledAppointmentFlag=1 and pat.["
                                        "PatientNumber]=?  and ScheduledDate < ? and ScheduledDate is not null and his.ConfirmedFlag=1 "
                                        "order by ScheduledDate ASC;", [self.oldpatientnumber, currentDate])
                                    viewpastrecords = cursor.fetchall()
                                    if len(viewpastrecords) != 0:
                                        viewpastrecordslist.append(viewpastrecords)
                                elif ViewScheduledDate >= currentDate:
                                    cursor.execute("SELECT his.[AppointmentID],pat.PatientNumber,DoctorName,ScheduledDate,ScheduledTime,CASE WHEN CAST(ScheduledTime as "
                                                   "int) >=12 THEN 'PM'  WHEN CAST(ScheduledTime as int) < 12  THEN 'AM' END as Timezone FROM PatientAppointment as his "
                                                   "inner join PatientData as pat on his.PatientNumber=pat.PatientNumber where ScheduledAppointmentFlag=1 and pat.["
                                                   "PatientNumber]=?  and  ScheduledDate >= ? and ScheduledDate is not null and "
                                                   "his.ConfirmedFlag=1 order by ScheduledDate ASC;", [self.oldpatientnumber, currentDate])
                                    viewcurrentrecords = cursor.fetchall()
                                    if len(viewcurrentrecords) != 0:
                                        viewcurrentrecordslist.append(viewcurrentrecords)
                            ####### Display for both current and Past Appointment details ##########
                            if len(viewpastrecordslist) >= 1:
                                print("\n Below are your past appointment details : ")
                                for pastrowdetail in viewpastrecordslist:
                                    for pastrows in pastrowdetail:
                                        print('\t AppointmentID:' + str(pastrows[0]) + '\tPatient Number:' + str(pastrows[1]) + '\t Doctor Name:' + str(
                                            pastrows[2]) +
                                              '\t  Date:' + str(pastrows[3]) + '\t  Time:' + str(pastrows[4]) + ' ' + str(pastrows[5]))
                            else:
                                print("\n No past appointment details.")

                            print("-----------------------------------------------------------------------------------------------------------------")
                            if len(viewcurrentrecordslist) >= 1:
                                print("Below are your current and future appointment details : ")
                                for currentrowdetails in viewcurrentrecordslist:
                                    for currrow in currentrowdetails:
                                        print('\t AppointmentID:' + str(currrow[0]) + '\tPatient Number:' + str(currrow[1]) + '\t Doctor Name:' + str(
                                            currrow[2]) +
                                              '\t  Date:' + str(currrow[3]) + '\t  Time:' + str(currrow[4]) + ' ' + str(currrow[5]))
                            else:
                                print("\n No current and future appointments scheduled.")

                    # -------------------------------- To View the Prescriptions ---------------------------------
                    # dataset : PrescriptionDate must be same as ScheduledDate
                    if input_value_ASK == 4:
                        cursor.execute("select exists (SELECT PatientNumber FROM prescription where [PatientNumber]=?) as flag", [self.oldpatientnumber])
                        appointment_details = cursor.fetchone()
                        if appointment_details[0] == 0:
                            print("\n No Prescription details to view.")
                        else:
                            cursor.execute("SELECT prescription_date FROM prescription as prc where PatientNumber=? and AppointmentID is not null and prescription is "
                                           "not null", [self.oldpatientnumber])
                            prescriptiodate = cursor.fetchall()
                            uniqueprescriptiodate = set(prescriptiodate)
                            viewpastprescriptionlist = []
                            viewcurrentprescriptionlist = []

                            for uniqueprescriptionrecords in uniqueprescriptiodate:
                                stringprescriptiondate = ''.join(uniqueprescriptionrecords)
                                ViewPrescriptionDate = datetime.strptime(stringprescriptiondate, '%Y-%m-%d').date()
                                if ViewPrescriptionDate < currentDate:
                                    cursor.execute(
                                        "select  prc.AppointmentID,pat.PatientNumber, pat.FirstName ||' ' || pat.LastName as Fullname,his.DoctorName,his.ScheduledDate,"
                                        "his.ScheduledTime,CASE WHEN CAST(ScheduledTime as int) >=12 THEN 'PM'  WHEN CAST(ScheduledTime as int) < 12  THEN 'AM' END as "
                                        "Timezone,prc.prescription from prescription as prc inner join PatientData as pat on "
                                        "prc.PatientNumber=pat.PatientNumber inner join PatientAppointment as his on his.PatientNumber=pat.PatientNumber and "
                                        "his.[AppointmentID]=prc.AppointmentID where "
                                        " prc.PatientNumber=? and pat.ScheduledAppointmentFlag=1 and  his.ConfirmedFlag=1 and ScheduledDate<? order by ScheduledDate ASC",
                                        [self.oldpatientnumber, currentDate])
                                    viewprescriptionpastrecords = cursor.fetchall()
                                    if len(viewprescriptionpastrecords) != 0: 
                                        viewpastprescriptionlist.append(viewprescriptionpastrecords)

                                elif ViewPrescriptionDate >= currentDate:
                                    cursor.execute(
                                        "select  prc.AppointmentID,pat.PatientNumber, pat.FirstName ||' ' || pat.LastName as Fullname,his.DoctorName,his.ScheduledDate,"
                                        "his.ScheduledTime,CASE WHEN CAST(ScheduledTime as int) >=12 THEN 'PM'  WHEN CAST(ScheduledTime as int) < 12  THEN 'AM' END as "
                                        "Timezone,prc.prescription from prescription as prc inner join PatientData as pat on "
                                        "prc.PatientNumber=pat.PatientNumber inner join PatientAppointment as his on his.PatientNumber=pat.PatientNumber and his.["
                                        "AppointmentID]=prc.AppointmentID where "
                                        " prc.PatientNumber=? and pat.ScheduledAppointmentFlag=1 and ScheduledDate>=? and his.ConfirmedFlag=1 order by ScheduledDate ASC",
                                        [self.oldpatientnumber, currentDate])
                                    viewpresentprescriptionrecords = cursor.fetchall()
                                    if len(viewpresentprescriptionrecords) != 0:
                                        viewcurrentprescriptionlist.append(viewpresentprescriptionrecords)

                            if len(viewpastprescriptionlist) >= 1:
                                print("\n Below are your past prescriptions details : ")
                                for prcpastrowdetail in viewpastprescriptionlist:
                                    for prcpastrows in prcpastrowdetail:
                                        print('\t Appointment-ID:' + str(prcpastrows[0]) + '\t Patient-Number:' + str(prcpastrows[1]) + '\t Patient-Name:' + str(
                                            prcpastrows[2]) + '\t Doctor-Name :' + str(prcpastrows[3]) + '\t  Date:' + str(prcpastrows[4]) + '\t Time:' + str(
                                            prcpastrows[5]) + ' ' + str(prcpastrows[6]) + '\t Prescriptions:' + str(prcpastrows[7]))
                            else:
                                print("\n No past prescriptions details.")
                            print(
                                "\n--------------------------------------------------------------------------------------------------------------------------------------------------")
                            if len(viewcurrentprescriptionlist) >= 1:
                                print("\n Below are your current prescriptions details : ")
                                for prccurrentrowdetails in viewcurrentprescriptionlist:
                                    for prccurrrow in prccurrentrowdetails:
                                        print('\t Appointment-ID:' + str(prccurrrow[0]) + '\t Patient-Number:' + str(prccurrrow[1]) + '\t Patient-Name:' + str(
                                            prccurrrow[2]) +
                                              '\t Doctor-Name :' + str(prccurrrow[3]) + '\t  Date:' + str(prccurrrow[4]) + '\t Time:' + str(
                                            prccurrrow[5]) + ' ' + str(prccurrrow[6]) + '\t Prescriptions:' + str(prccurrrow[7]))
                            else:
                                print("\n No current prescriptions available.")

                    # -------------------------------- To View the cancelled appointment details ---------------------------------
                    # dataset : ScheduledDate must be 3 from patient_Data table and ConfirmedFlag must be 2 in PatientAppointment table.
                    if input_value_ASK == 5:
                        cursor.execute("select count(*) from PatientAppointment where PatientNumber=? and ConfirmedFlag in(2,3)", [self.oldpatientnumber])
                        cancelledappointment_details = cursor.fetchone()
                        if cancelledappointment_details[0] == 0:
                            print("\n No Cancelled appointment details to view.")
                        else:
                            print("Below are Your Cancelled Appointment Details")
                            print("-----------------------------------------------------------------------------------------------------------------")
                            cursor.execute("select pat.PatientNumber,app.AppointmentID,app.DoctorName,app.ScheduledDate,app.ScheduledTime,CASE WHEN CAST(ScheduledTime "
                                           "as int) >=12 THEN 'PM'  WHEN CAST(ScheduledTime as int) < 12  THEN 'AM' END as Timezone from PatientData as pat inner join "
                                           "PatientAppointment as app on pat.PatientNumber=app.PatientNumber where pat.PatientNumber=? and  (app.ConfirmedFlag in(2,3)) order by ScheduledDate ASC",
                                           [self.oldpatientnumber])
                            ViewCancelledrecords = cursor.fetchall()
                            for Cancelledrecords in ViewCancelledrecords:
                                print('\t Patient-Number:' + str(Cancelledrecords[0]) + '\t Appointment-ID:' + str(Cancelledrecords[1]) +
                                      '\t Doctor-Name :' + str(Cancelledrecords[2]) + '\t  Date:' + str(Cancelledrecords[3]) + '\t Time:' + str(
                                    Cancelledrecords[4]) + str(Cancelledrecords[5]))

                    self.audit(self.oldpatientnumber)

        patientdetatails.logout()

    def logout(self):
        error_logout = True
        while error_logout:
            logout = str(input("\n Do you want to Logout :").upper())
            if logout == '' or not logout in ('YES', 'NO'):
                print('Please answer with yes or no!')
            else:
                error_logout = False
            if logout == "YES":
                print("Logged out successfully!")
            elif logout == "NO":
                patientdetatails.requestUserInput(self.existing_email, self.oldpatientnumber)

    # -------------------------------- Audit the patient Data (Patient-Number,[AppointmentID],PrimarySymptoms,OtherSymptoms---------------------------------
    def audit(self, recordspatientnumber):
        cursor.execute("select count(LOGID) from PatientLog where PatientNumber=? ;", [recordspatientnumber])
        logid = cursor.fetchone()
        if logid[0] == 0:
            cursor.execute("INSERT INTO PatientLog(PatientNumber) VALUES (?) ", [recordspatientnumber])
            sqlConnection.commit()

        else:
            cursor.execute('select count(PatientNumber) from PatientAppointment where PatientNumber=?;', [recordspatientnumber])
            patnum = cursor.fetchone()[0]

            if patnum == 1:
                cursor.execute('select [AppointmentID],PrimarySymptoms,OtherSymptoms,DoctorName,ScheduledDate,ScheduledTime,ConfirmedFlag from PatientAppointment where '
                               'PatientNumber=? order by [AppointmentID] LIMIT 1;', [recordspatientnumber])
                app_id = cursor.fetchall()
                for appointments in app_id:
                    # First Record is updated as we have already row inserted in the table from registration step.
                    cursor.execute("UPDATE PatientLog SET AppointmentID=?,PrimarySymptoms=?,OtherSymptoms=? where  PatientNumber=?;",
                                   [appointments[0], appointments[1], appointments[2], recordspatientnumber])
                    sqlConnection.commit()

            elif patnum > 1:
                cursor.execute(
                    'select PatientNumber,[AppointmentID],PrimarySymptoms,OtherSymptoms,DoctorName,ScheduledDate,ScheduledTime,ConfirmedFlag from PatientAppointment where '
                    'PatientNumber=? and [AppointmentID] not in  (select AppointmentID FROM PatientLog where PatientNumber=?) order by [AppointmentID];',
                    [recordspatientnumber, recordspatientnumber])
                app_id = cursor.fetchall()
                for appointments in app_id:
                    cursor.execute("INSERT INTO PatientLog (PatientNumber,AppointmentID,PrimarySymptoms,OtherSymptoms) VALUES (?,?,?,?) ",
                                   [recordspatientnumber, appointments[1], appointments[2], appointments[3]])
                    sqlConnection.commit()



# -- Staff Module Starts Here --

def Symp_Query(PSymp):
    Symp_Query = cursor.execute(
        "SELECT COUNT(DC.DOC_ID) FROM DOCTOR_CALENDAR DC INNER JOIN DEPARTMENTS DP ON DC.DEPARTMENT = DP.DEPARTMENT_NAME WHERE DC.AVAILABLITY = 1 AND DP.SYMPTOMPS LIKE ? ",
        ['%' + PSymp + '%', ])
    Sym_Q = Symp_Query.fetchall()
    if Sym_Q is None:
        return None
    else:
        return Sym_Q


def Symp_Dept(PSympts):
    Symp_Dept = cursor.execute("select count(DEPARTMENT_NAME) from DEPARTMENTS where SYMPTOMPS LIKE ? ",
                               ['%' + PSympts + '%', ])
    SymDept = Symp_Dept.fetchone()
    if SymDept is None:
        return None
    else:
        return SymDept


def Full_Query(FullSymp):
    Full_Query = cursor.execute(
        "SELECT DC.DOC_ID,DC.DOC_NAME, DC.DEPARTMENT,DC.DATE,DC.SHIFT_TYPE,DC.TIME_SLOT_START,DC.TIME_SLOT_END,DC.SLOT FROM DOCTOR_CALENDAR DC INNER JOIN DEPARTMENTS DP ON DC.DEPARTMENT = DP.DEPARTMENT_NAME WHERE DC.AVAILABLITY = 1 AND DP.SYMPTOMPS LIKE ? ",
        ['%' + FullSymp + '%', ])
    Sym_F = Full_Query.fetchall()
    if Sym_F != 0:
        return Sym_F
    else:
        return None


def Fetch_Login(Login_ID):
    Fetch_Login = cursor.execute("SELECT STAFF_ID, PASSWORD, ACCESS_COUNT FROM STAFF_USERS WHERE STAFF_ID = ?",
                                 (Login_ID,))
    Existing_Login = Fetch_Login.fetchone()
    if Existing_Login is None:
        return None
    else:
        return Existing_Login

# -- Admin Module Starts Here --
class AdminModule:
    def admin_user_login(self, admin_main):
        user_id = input("Enter your User Id: ").upper()
        user_pwd = input("Enter your Password: ")
        user_type = "ADMIN"

        # User login will be unique irrespective of the casing
        # Password is case-sensitive

        connection = sqlite3.connect("Walk-In-Clinic-DB.db")

        # Fetching existing data for login validation
        cursor = connection.cursor()
        cursor.execute("SELECT ADMIN_ID, PASSWORD, USER_TYPE  FROM ADMIN_USERS;")
        results_login = cursor.fetchall()
        cursor.close()

        flag1 = 0

        for r in results_login:
            if user_id == r[0] and user_pwd == r[1] and user_type == r[2]:
                flag1 = 1
                print(
                    "Welcome to our login system, user {}!".format(r[0]))
                break
            else:
                flag1 = 0

        if flag1 == 0:
            print("ERROR: Either your Email ID and password are incorrect or user isn't an admin user!!!!! Exiting....")
            connection.close()
            return 1

        # Updating access count in DB for Audit purpose
        cursor = connection.cursor()
        cursor.execute("UPDATE ADMIN_USERS SET ACCESS_COUNT = ACCESS_COUNT +1 WHERE ADMIN_ID = ? AND PASSWORD=?;",
                       (user_id, user_pwd))
        connection.commit()
        cursor.close()

        connection.close()

        choice = 0
        while choice != 5:
            try:
                choice = int(input(
                    "\nWelcome to Admin Login System! \n Press 1 to add a new Doctor user. \n Press 2 to add a new Staff user. \n Press 3 to view Doctors' calendar. \n Press 4 to update Doctors' calendar. \n Press 5 to exit.\n"))

                if choice == 1:
                    admin_main.new_doctor_user()
                elif choice == 2:
                    admin_main.new_staff_user()
                elif choice == 3:
                    admin_main.view_doctor_calendar()
                elif choice == 4:
                    admin_main.input_doctor_calendar()
                elif choice == 5:
                    print("Thank You for Visiting!!")
                    break
                else:
                    print("ERROR: You have entered wrong input! Please try again.")
            except ValueError:
                print("ERROR: You have entered wrong input! Please try again. Exiting.....")

        return 0

    def new_doctor_user(self):

        user_type = "DR"
        user_name = input("Enter Doctor's Name: ")
        user_email = input("Enter Doctor's Email: ")
        connection = sqlite3.connect("Walk-In-Clinic-DB.db")

        # Department Check
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT(DEPARTMENT_NAME) FROM DEPARTMENTS;")
        results_dept = cursor.fetchall()
        cursor.close()

        dept_dict = {}
        try:
            if results_dept:
                flag1 = 0
                count1 = 1
                for r in results_dept:
                    doc_dept = str(r)
                    doc_dept = doc_dept[2:-3]
                    print("Press {0} to choose the department {1}".format(count1, doc_dept))
                    dept_dict[count1] = doc_dept
                    count1 += 1
                user_choice = int(input("Enter your choice for Doctor's Department: "))

                while flag1 == 0:
                    if user_choice not in dept_dict.keys():
                        print("Your choice is incorrect, Please choose again.")
                        user_choice = int(input("Enter your choice for Doctor's Department: "))
                        flag1 = 0
                        continue
                    else:
                        user_dept = dept_dict[user_choice]
                        print("Your choice of department is: " + user_dept)
                        flag1 = 1
                        break
        except ValueError:
            print("Invalid string input, Exiting....")
            return 1

        # Duplicate Check
        cursor = connection.cursor()
        cursor.execute("SELECT DOC_ID  FROM DOCTOR_USERS;")
        results_login = cursor.fetchall()
        cursor.close()

        user_id = random.randint(10000, 99999)
        user_id = 'DR' + str(user_id)

        if results_login:
            flag1 = 0
            while flag1 == 0:
                for r in results_login:
                    if user_id in r:
                        user_id = random.randint(10000, 99999)
                        user_id = 'DR' + str(user_id)
                        flag1 = 0
                        break
                    else:
                        flag1 = 1
        user_pwd = user_id

        initial_access_count = 0

        # Inserting new credentials in DB
        cursor = connection.cursor()
        cursor.execute("INSERT INTO DOCTOR_USERS ( DOC_ID, PASSWORD, USER_TYPE, ACCESS_COUNT) VALUES (?, ?, ?, ?)",
                       (user_id, user_pwd, user_type, initial_access_count))
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("INSERT INTO DOCTOR_DETAILS(DOC_ID, DOC_NAME, DEPARTMENT, EMAIL) VALUES (?, ?, ?, ?)",
                       (user_id, user_name, user_dept, user_email))
        connection.commit()
        cursor.close()

        connection.close()
        print("A new doctor user has been created with Doctor Number:{} and Password:{}!".format(user_id, user_pwd))
        return 0

    def new_staff_user(self):

        user_type = "ST"
        user_name = input("Enter Staff's Name: ")
        user_email = input("Enter Staff's Email: ")
        connection = sqlite3.connect("Walk-In-Clinic-DB.db")

        # Duplicate Check
        cursor = connection.cursor()
        cursor.execute("SELECT STAFF_ID FROM STAFF_USERS;")
        results_login = cursor.fetchall()
        cursor.close()

        user_id = random.randint(10000, 99999)
        user_id = 'ST' + str(user_id)

        if results_login:
            flag1 = 0
            while flag1 == 0:
                for r in results_login:
                    if user_id in r:
                        user_id = random.randint(10000, 99999)
                        user_id = 'ST' + str(user_id)
                        flag1 = 0
                        break
                    else:
                        flag1 = 1
        user_pwd = user_id

        # Inserting new credentials in DB
        cursor = connection.cursor()
        cursor.execute("INSERT INTO STAFF_USERS ( STAFF_ID, PASSWORD, USER_TYPE ) VALUES (?, ?, ?)",
                       (user_id, user_pwd, user_type))
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("INSERT INTO STAFF_DETAILS( STAFF_ID, STAFF_NAME, EMAIL ) VALUES (?, ?, ?)",
                       (user_id, user_name, user_email))
        connection.commit()
        cursor.close()

        connection.close()
        print("A new staff member has been created with Staff Number:{} and Password:{}!".format(user_id, user_pwd))
        return 0

    def view_doctor_calendar(self):

        connection = sqlite3.connect("Walk-In-Clinic-DB.db")
        doc_id = str(input("Enter Doctor's ID ")).upper()

        cursor = connection.cursor()
        cursor.execute("SELECT DOC_ID FROM DOCTOR_USERS;")
        results_login = cursor.fetchall()
        cursor.close()

        flag1 = 0
        if results_login:
            while flag1 == 0:
                for r in results_login:
                    if doc_id in r:
                        flag1 = 2
                        break
                    else:
                        flag1 = 1
        if flag1 == 2:
            print("This Doctor ID is Valid, Proceeding...")
        elif flag1 == 1 or flag1 == 0:
            print("ERROR: This Doctor ID is Invalid, Please check!!!!! Exiting......")
            return 1

        cursor = connection.cursor()
        cursor.execute(
            "SELECT DATE, SHIFT_TYPE, TIME_SLOT_START, PATIENT_NUMBER FROM DOCTOR_CALENDAR WHERE DOC_ID = ?;",
            (doc_id,))
        results_data = cursor.fetchall()
        cursor.close()

        if results_data:
            print("-------------------------------------------------------")
            print("| DATE    | Shift Type | Slot Start Time | Patient No.|")
            for r in results_data:
                print("-------------------------------------------------------")
                print("| " + str(r[0]) + "  |  " + str(r[1]) + "    |    " + str(r[2]) + "  |  " + str(r[3]) + " |")
            print("-------------------------------------------------------")
        else:
            print("No calendar entries for this Doctor ID are present!!!!")

        connection.close()
        return 0

    def input_doctor_calendar(self):

        connection = sqlite3.connect("Walk-In-Clinic-DB.db")
        doc_id = str(input("Enter Doctor's ID ")).upper()

        cursor = connection.cursor()
        cursor.execute("SELECT DOC_ID FROM DOCTOR_USERS;")
        results_login = cursor.fetchall()
        cursor.close()

        flag1 = 0
        if results_login:
            while flag1 == 0:
                for r in results_login:
                    if doc_id in r:
                        flag1 = 2
                        break
                    else:
                        flag1 = 1
        if flag1 == 2:
            print("This Doctor ID is Valid, Proceeding...")
        elif flag1 == 1 or flag1 == 0:
            print("ERROR: This Doctor ID is Invalid, Please check!!!!! Exiting......")
            return 1

        # Fetching DOC_NAME from DOCTOR_DETAILS table to insert in Calendar Table
        cursor = connection.cursor()
        cursor.execute("SELECT DOC_NAME FROM DOCTOR_DETAILS WHERE DOC_ID = ?;", (doc_id,))
        result_doc_name = cursor.fetchone()
        cursor.close()

        doc_name = str(result_doc_name)
        doc_name = doc_name[2:-3]

        # Fetching DEPARTMENT from DOCTOR_DETAILS table to insert in Calendar Table
        cursor = connection.cursor()
        cursor.execute("SELECT DEPARTMENT FROM DOCTOR_DETAILS WHERE DOC_ID = ?;", (doc_id,))
        result_doc_dept = cursor.fetchone()
        cursor.close()

        doc_dept = str(result_doc_dept)
        doc_dept = doc_dept[2:-3]

        shift_year = int(input("Enter the Year for the shift in the format YYYY, Example: 2022 - "))
        shift_month = int(input("Enter the Month for the shift in the format MM, Example: 04 - "))
        shift_day = int(input("Enter the Date for the shift in the format DD, Example: 30 - "))

        # Date Validity check
        try:
            shift_date = date(shift_year, shift_month, shift_day)
        except Exception as e:
            print("ERROR: " + str(e) + "!!!!! Exiting....")
            return 1

        # Validate that Date is either current or future date
        today = date.today()
        if shift_date >= today:
            print("Date is Valid, Proceeding... ")
        else:
            print("ERROR: Cannot Insert records for a past date!!!! Exiting.....")
            return 1

        # Insert availability for a particular number of days
        consecutive_days = int(
            input("Enter number of days you want to repeat this schedule consecutively after this date: "))
        choice = int(input(
            "Please enter doctor's shift slot : \n Press 1 for Morning slot \n Press 2 for Afternoon slot \n Press 3 for Evening slot \n"))
        if choice == 1:
            doc_shift = "Morning"
        elif choice == 2:
            doc_shift = "Afternoon"
        elif choice == 3:
            doc_shift = "Evening"
        else:
            print("ERROR: Invalid Input!!!! Exiting.....")
            return 1

        # Date value is present in DB or not check if consecutive_days >=1
        try:
            for i in range(0, consecutive_days + 1):
                consecutive_shift_date = shift_date + timedelta(days=i)

                cursor = connection.cursor()
                cursor.execute(
                    "SELECT DOC_ID, DATE, SHIFT_TYPE FROM DOCTOR_CALENDAR WHERE DOC_ID = ? AND DATE = ? AND SHIFT_TYPE = ? ;",
                    (doc_id, consecutive_shift_date, doc_shift))
                results_shift = cursor.fetchall()
                cursor.close()

                if results_shift:
                    print("Availability is already present for {0} date slot!".format(consecutive_shift_date))
                    print("Please check your date or fix the consecutive days. Exiting....")
                    return 1
                else:
                    print("No existing entry for", consecutive_shift_date,
                          "for this shift and Doctor Id. Proceeding....")
        except Exception as e:
            print("ERROR: " + str(e) + "!!!!! Exiting....")
            return 1

        # Insertion of the slots post validations
        try:
            if choice == 1:
                # Morning Shift
                for i in range(0, consecutive_days + 1):
                    consecutive_shift_date = shift_date + timedelta(days=i)
                    print("Adding shift for date", consecutive_shift_date)
                    slot_num = 1
                    for j in range(10, 12):
                        start_time = time(j, 0)
                        end_time = time(start_time.hour + 1, 0)
                        end_time = str(end_time)
                        start_time = str(start_time)
                        slot = "SLOT" + str(slot_num)
                        cursor = connection.cursor()
                        cursor.execute(
                            "INSERT INTO DOCTOR_CALENDAR(DOC_ID, DOC_NAME, DATE, SHIFT_TYPE, TIME_SLOT_START, TIME_SLOT_END, SLOT, DEPARTMENT) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (doc_id, doc_name, consecutive_shift_date, doc_shift, start_time, end_time, slot, doc_dept))
                        connection.commit()
                        cursor.close()
                        slot_num += 1

            elif choice == 2:
                # Afternoon Shift
                for i in range(0, consecutive_days + 1):
                    consecutive_shift_date = shift_date + timedelta(days=i)
                    print("Adding shift for date", consecutive_shift_date)
                    slot_num = 3
                    for j in range(14, 16):
                        start_time = time(j, 0)
                        end_time = time(start_time.hour + 1, 0)
                        end_time = str(end_time)
                        start_time = str(start_time)
                        slot = "SLOT" + str(slot_num)
                        cursor = connection.cursor()
                        cursor.execute(
                            "INSERT INTO DOCTOR_CALENDAR(DOC_ID, DOC_NAME, DATE, SHIFT_TYPE, TIME_SLOT_START, TIME_SLOT_END, SLOT, DEPARTMENT) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (doc_id, doc_name, consecutive_shift_date, doc_shift, start_time, end_time, slot, doc_dept))
                        connection.commit()
                        cursor.close()
                        slot_num += 1

            elif choice == 3:
                # Evening Shift
                for i in range(0, consecutive_days + 1):
                    consecutive_shift_date = shift_date + timedelta(days=i)
                    print("Adding shift for date", consecutive_shift_date)
                    slot_num = 5
                    for j in range(17, 19):
                        start_time = time(j, 0)
                        end_time = time(start_time.hour + 1, 0)
                        end_time = str(end_time)
                        start_time = str(start_time)
                        slot = "SLOT" + str(slot_num)
                        cursor = connection.cursor()
                        cursor.execute(
                            "INSERT INTO DOCTOR_CALENDAR(DOC_ID, DOC_NAME, DATE, SHIFT_TYPE, TIME_SLOT_START, TIME_SLOT_END, SLOT, DEPARTMENT) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (doc_id, doc_name, consecutive_shift_date, doc_shift, start_time, end_time, slot, doc_dept))
                        connection.commit()
                        cursor.close()
                        slot_num += 1
            else:
                print("ERROR: Invalid Input!!!! Exiting.....")
                return 1
        except Exception as e:
            print("ERROR: " + str(e) + "!!!!! Exiting....")
            return 1
        connection.close()
        return 0


# -- Admin Module Ends Here --

class StaffModule:
    def Pt_Count(self):
        Pt_Count = cursor.execute(
            "SELECT count(A.PatientNumber) FROM PatientAppointment A, PatientData B on A.PatientNumber = B.PatientNumber WHERE A.Confirmedflag= 0 and (A.DOCTORNAME is null OR A.DOCTORNAME = '') ")
        Chk_Cnt = Pt_Count.fetchone()
        if Chk_Cnt is None:
            return None
        else:
            return Chk_Cnt

    def Pt_Details(self):
        Pt_Details = cursor.execute(
            "select A.[AppointmentID], A.PatientNumber, A.PrimarySymptoms,OtherSymptoms FROM PatientAppointment A, PatientData B on A.PatientNumber = B.PatientNumber WHERE A.Confirmedflag= 0 and (A.DOCTORNAME is null OR A.DOCTORNAME = '') ")
        Chk_Dtls = Pt_Details.fetchall()
        if Chk_Dtls is None:
            return None
        else:
            return Chk_Dtls

    def Other_Symp(self):
        Other_Symp = cursor.execute(
            "SELECT COUNT(DC.DOC_ID) FROM DOCTOR_CALENDAR DC INNER JOIN DEPARTMENTS DP ON DC.DEPARTMENT = DP.DEPARTMENT_NAME WHERE DC.AVAILABLITY = 1 AND DP.SYMPTOMPS = 'OTHERS' ")
        SymOther = Other_Symp.fetchone()
        if SymOther is None:
            return None
        else:
            return SymOther

    def Full_Symp(self):
        Full_Symp = cursor.execute(
            "SELECT DC.DOC_ID,DC.DOC_NAME,DC.DEPARTMENT,DC.DATE,DC.SHIFT_TYPE,DC.TIME_SLOT_START,DC.TIME_SLOT_END,DC.SLOT FROM DOCTOR_CALENDAR DC INNER JOIN DEPARTMENTS DP ON DC.DEPARTMENT = DP.DEPARTMENT_NAME WHERE DC.AVAILABLITY = 1 AND DP.SYMPTOMPS = 'OTHERS' ")
        SymOther = Full_Symp.fetchall()
        if SymOther is None:
            return None
        else:
            return SymOther

    def Cancel_Count(self):
        Cancel_Count = cursor.execute("SELECT count(PatientNumber) FROM PatientAppointment WHERE Confirmedflag= 2 ")
        Cnl_Cnt = Cancel_Count.fetchone()
        if Cnl_Cnt is None:
            return None
        else:
            return Cnl_Cnt

    def Cancel_Check(self):
        Cancel_Check = cursor.execute(
            "SELECT [AppointmentID], PatientNumber, DoctorName, ScheduledDate, ScheduledTime FROM PatientAppointment WHERE Confirmedflag= 2 ")
        Cnl_Chk = Cancel_Check.fetchall()
        if Cnl_Chk is None:
            return None
        else:
            return Cnl_Chk

if __name__ == '__main__':
    print("\n ***************  Welcome to Walk-in Clinic! Please Choose From Below Options. *****************")
    while True:

        print("\n Please pick your choice from below :")
        print("\n Enter 1 for Patients: ")
        print("\n Enter 2 for Staff: ")
        print("\n Enter 3 for Doctors: ")
        print("\n Enter 4 for Admin: ")
        print("\n Enter 5 to Exit ")
        try:
            mod_input = int(input("\n please provide your input:"))
            if mod_input == 1:
                print("\n *************************************************  Welcome to Patient Module!  *************************************** ")
                print("\n ********************* Please enter the following details to avail many preventive health services. *********************")

                exp_status = True
                while exp_status:
                    try:
                        print("\n Please Provide below details to Register Or login.")
                        patientdetatails = PatientModule()
                        error_status = True
                        error_con_ASK = True

                        while error_status:
                            bool_status = str(input(
                                " \n Are you a new Patient? \n Enter YES To Register \n\t\tNO To Login\n\t\t ").upper())
                            if bool_status == '' or not bool_status in ('YES', 'NO'):
                                print('Please answer with yes or no!')
                            else:
                                error_status = False

                                if bool_status == 'YES':
                                    patientdetatails.patientRegistration()

                                elif bool_status == 'NO':
                                    patientdetatails.patientLogin()

                                error_con_ASK = True
                                while error_con_ASK:
                                    last_check = str(input("\n Do you want to continue :").upper())
                                    if last_check == '' or not last_check in ('YES', 'NO'):
                                        print('Please answer with yes or no!')
                                    else:
                                        error_con_ASK = False
                                    if last_check == "YES":
                                        error_status = True

                                    elif last_check == "NO":

                                        break
                        exp_status = False
                        break
                    except:
                        Return_Menu = input("Press ENTER KEY to go back to Main Menu")
                        break
                continue

            elif mod_input == 2:
                print("\n Please verify your Staff Login ")
                while True:
                    try:
                        Curr_Login = str(input("\n Enter your Staff ID : ")).upper()
                        XLogin = Fetch_Login(Curr_Login)
                        if XLogin[0] is not None:
                            Access_Count = XLogin[2] + 1
                            print("")
                            print("Staff ID exists, please proceed with the below: ")
                            print("")
                            while True:
                                try:
                                    Ext_Pswrd = str(input("Enter your Password :")).upper()
                                    Login_Check = Fetch_Login(Curr_Login)
                                    if Ext_Pswrd == Login_Check[1]:
                                        cursor.execute("UPDATE STAFF_USERS SET ACCESS_COUNT = ? WHERE STAFF_ID = ? ",
                                                       (Access_Count, Curr_Login))
                                        sqlConnection.commit()
                                        print("**********************************")
                                        print("You have logged in successfully !! ")
                                        print("")
                                        print("Dear", Curr_Login, ", you can now book appointments to the patients")
                                        print("")
                                        Return_Menu = input("Press ENTER KEY to see the Menu options")
                                        # break

                                        while True:
                                            print("\n ====== Please choose the below options ======")
                                            print("\n Enter 1 to View Appointment Details")
                                            print("\n Enter 2 to Book an Appointment")
                                            print("\n Enter 3 to Cancel Appointment")
                                            print("\n Enter 4 to go back to Main Menu")
                                            staff_input = input("\n Please enter your choice : ")
                                            print("")
                                            StaffDetails = StaffModule()
                                            if staff_input == "1":
                                                while True:
                                                    try:
                                                        Check_Result = StaffDetails.Pt_Count()
                                                        if Check_Result[0] >= 1:
                                                            print("There are " + str(Check_Result[
                                                                                         0]) + " patient(s) waiting to book an appointment:")
                                                            print("")
                                                            View_Result = StaffDetails.Pt_Details()
                                                            for PntDtls in View_Result:
                                                                AppointmentID = PntDtls[0]
                                                                PatientNumber = PntDtls[1]
                                                                PrimarySymptoms = PntDtls[2]
                                                                SecondarySymptoms = PntDtls[3]
                                                                temp_list = [AppointmentID, PatientNumber,
                                                                             PrimarySymptoms, SecondarySymptoms]
                                                                mydata.append(temp_list)
                                                                head = ["Appointment ID", "Patient Number",
                                                                        "Primary Symptomps", "Other Symptomps"]

                                                            print(tabulate(mydata, headers=head, tablefmt="grid"))
                                                            print("")
                                                            Return_Menu = input(
                                                                "Go back to main menu to Book and Appointment. Press ENTER KEY to go back to Main Menu")
                                                            break
                                                        else:
                                                            print(
                                                                "There are no patients waiting to book an appointment")
                                                            print("")
                                                            Return_Menu = input(
                                                                "Press ENTER KEY to go back to Main Menu")
                                                            break
                                                    except:
                                                        print(
                                                            "Invalid option. Please choose the options between 1 to 3")
                                                        print("")
                                                        Return_Menu = input("Press ENTER KEY to go back to Main Menu")
                                                        break

                                            elif staff_input == "2":
                                                while True:
                                                    try:
                                                        # The below code will update doctors availability if date is less than current date
                                                        today = date.today()
                                                        cursor.execute(
                                                            "update DOCTOR_CALENDAR set AVAILABLITY = 0 where DATE < ? ",
                                                            [today])
                                                        sqlConnection.commit()

                                                        StaffDetails = StaffModule()
                                                        Count_Result = StaffDetails.Pt_Count()
                                                        if Count_Result[0] >= 1:
                                                            print("There are " + str(
                                                                Count_Result[0]) + " patient(s) available to book.")
                                                            Book_Result = StaffDetails.Pt_Details()
                                                            print(
                                                                "Please book the appointment for the below patient(s) ")
                                                            head = ["Appointment ID", "Patient Number",
                                                                    "Primary Symptomps", "Other Symptomps"]
                                                            AppointmentID_list = []
                                                            mydata = []
                                                            for SYMP in Book_Result:
                                                                AppointmentID = SYMP[0]
                                                                PatientNumber = SYMP[1]
                                                                PrimarySymptoms = SYMP[2]
                                                                SecondarySymptoms = SYMP[3]
                                                                temp_list = [AppointmentID, PatientNumber,
                                                                             PrimarySymptoms, SecondarySymptoms]
                                                                mydata.append(temp_list)

                                                                AppointmentID_list.append(AppointmentID)
                                                            print(tabulate(mydata, headers=head, tablefmt="grid"))

                                                            while n == 1:
                                                                try:
                                                                    App_Input = int(input(
                                                                        "\nPlease enter the appointment ID to view the doctors availabilty :"))
                                                                    print("")
                                                                    if App_Input in AppointmentID_list:
                                                                        print(
                                                                            "Appointment ID is valid, please check the below slots")
                                                                        print(
                                                                            "**************************************************")
                                                                        break
                                                                    else:
                                                                        raise Exception
                                                                except Exception:
                                                                    print("Appointment ID does not exists...")

                                                            cursor.execute(
                                                                "select PatientNumber,PrimarySymptoms from PatientAppointment where [AppointmentID] = ? ",
                                                                [App_Input])
                                                            DTLS = cursor.fetchall()
                                                            for PtnsSymps in DTLS:
                                                                PatientNumber = PtnsSymps[0]
                                                                PRMY_SMP = PtnsSymps[1].upper()
                                                                Infodtls = Symp_Dept(PRMY_SMP)
                                                                if Infodtls[0] == 0:
                                                                    print(
                                                                        "\nNew symptomp given by patient, assign a general physican for consultation")
                                                                    Doc_Av = StaffDetails.Other_Symp()
                                                                    if Doc_Av[0] == 0:
                                                                        cursor.execute(
                                                                            "update PatientAppointment set Confirmedflag = 3 where  PatientNumber = ? AND [AppointmentID] = ? ",
                                                                            [PatientNumber, App_Input])
                                                                        cursor.execute(
                                                                            "update PatientData set ScheduledAppointmentFlag = 2 where  PatientNumber = ? ",
                                                                            [PatientNumber])
                                                                        sqlConnection.commit()
                                                                        print(
                                                                            "\nNo Doctors are available to book an appointment.")
                                                                        print("")
                                                                    else:
                                                                        DocDTLS = StaffDetails.Full_Symp()
                                                                        DOCID_list = []
                                                                        SLOT_list = []
                                                                        DT_list = []
                                                                        head = ["DOCID", "DOCTORNAME", "DEPARTMENT",
                                                                                "DATE", "STARTTIME", "SLOT"]
                                                                        mydata = []
                                                                        for Fetch_Doc in DocDTLS:
                                                                            DOCID = Fetch_Doc[0]
                                                                            DOCTORNAME = Fetch_Doc[1]
                                                                            DEPARTMENT = Fetch_Doc[2]
                                                                            DATE = Fetch_Doc[3]
                                                                            SHIFT = Fetch_Doc[4]
                                                                            STARTTIME = Fetch_Doc[5]
                                                                            ENDTIME = Fetch_Doc[6]
                                                                            SLOT = Fetch_Doc[7]
                                                                            temp_list = [DOCID, DOCTORNAME, DEPARTMENT,
                                                                                         DATE, STARTTIME, SLOT]
                                                                            mydata.append(temp_list)
                                                                            DOCID_list.append(DOCID)
                                                                            DT_list.append(DATE)
                                                                            SLOT_list.append(SLOT)
                                                                        print(tabulate(mydata, headers=head,
                                                                                       tablefmt="grid"))

                                                                        Return_Menu = input(
                                                                            "Please ENTER KEY to start booking an appointment")
                                                                        while n == 1:
                                                                            try:
                                                                                DOC_ID = input(
                                                                                    "Enter Doctor ID: ").upper()
                                                                                if DOC_ID in DOCID_list:
                                                                                    print(
                                                                                        "Doctor ID exists, please proceed")
                                                                                    print("")
                                                                                    break
                                                                                else:
                                                                                    raise Exception
                                                                            except Exception:
                                                                                print(
                                                                                    "Doctor ID does not exists. Please recheck")

                                                                        while n == 1:
                                                                            try:
                                                                                DateInput = str(
                                                                                    input('Enter date(yyyy-mm-dd): '))
                                                                                if DateInput in DT_list:
                                                                                    print(
                                                                                        "Dates are valid, please proceed")
                                                                                    print("")
                                                                                    break
                                                                                else:
                                                                                    raise Exception
                                                                            except Exception:
                                                                                print(
                                                                                    "Incorrect date format. Please recheck")

                                                                        while n == 1:
                                                                            try:
                                                                                Enter_Slot = input(
                                                                                    "Select the slot number (Slot1, Slot2,..) ").upper()
                                                                                if Enter_Slot in SLOT_list:
                                                                                    cursor.execute(
                                                                                        "select DOC_ID,DATE,TIME_SLOT_START,DOC_NAME from DOCTOR_CALENDAR where DOC_ID = ? AND DATE = ? AND SLOT = ? ",
                                                                                        [DOC_ID, DateInput, Enter_Slot])
                                                                                    DTLS = cursor.fetchall()
                                                                                    print(DTLS)
                                                                                    for i in DTLS:
                                                                                        DOCTID = i[0]
                                                                                        DATE_TS = i[1]
                                                                                        STARTTIME = i[2]
                                                                                        DOCNAME = i[3]
                                                                                        print(DOCTID, DATE_TS,
                                                                                              STARTTIME)
                                                                                        cursor.execute(
                                                                                            "Update PatientData SET ScheduledAppointmentFlag = 1 WHERE PatientNumber = ? ",
                                                                                            [PatientNumber])
                                                                                        cursor.execute(
                                                                                            "UPDATE DOCTOR_CALENDAR SET PATIENT_NUMBER = ?, AVAILABLITY = 0 WHERE DOC_ID = ? AND DATE = ? AND SLOT = ? ",
                                                                                            [PatientNumber, DOCTID,
                                                                                             DATE_TS, Enter_Slot])
                                                                                        cursor.execute(
                                                                                            "update PatientAppointment set DoctorName= ?, ScheduledDate= ?, ScheduledTime= ? where  PatientNumber = ? AND [AppointmentID] = ? ",
                                                                                            [DOCNAME, DATE_TS, STARTTIME,
                                                                                             PatientNumber, App_Input])
                                                                                        sqlConnection.commit()
                                                                                        print(
                                                                                            "Appointment Booked Successfully----")
                                                                                        print("")
                                                                                        break
                                                                                    break
                                                                                else:
                                                                                    raise Exception
                                                                            except Exception:
                                                                                print(
                                                                                    "Incorrect input for slot, please enter valid slot id")
                                                                else:
                                                                    AVL = Full_Query(PRMY_SMP)
                                                                    if len(AVL) == 0 :
                                                                        cursor.execute(
                                                                            "update PatientAppointment set Confirmedflag = 3 where  PatientNumber = ? AND [AppointmentID] = ? ",
                                                                            [PatientNumber, App_Input])
                                                                        cursor.execute(
                                                                            "update PatientData set ScheduledAppointmentFlag = 2 where  PatientNumber = ? ",
                                                                            [PatientNumber])
                                                                        sqlConnection.commit()
                                                                        print(
                                                                            "\n No Doctors are available to book an appointment.")
                                                                        print("")
                                                                    else:
                                                                        FD = Full_Query(PRMY_SMP)
                                                                        DOC_list = []
                                                                        SLT_list = []
                                                                        mydata = []
                                                                        DT_list = []
                                                                        head = ["DOCID", "DOCTORNAME", "DEPARTMENT",
                                                                                "DATE", "STARTTIME", "SLOT"]
                                                                        for DC_AV in FD:
                                                                            DOCID = DC_AV[0]
                                                                            DOCTORNAME = DC_AV[1]
                                                                            DEPARTMENT = DC_AV[2]
                                                                            DATE = DC_AV[3]
                                                                            SHIFT = DC_AV[4]
                                                                            STARTTIME = DC_AV[5]
                                                                            ENDTIME = DC_AV[6]
                                                                            SLOT = DC_AV[7]
                                                                            temp_list = [DOCID, DOCTORNAME, DEPARTMENT,
                                                                                         DATE, STARTTIME, SLOT]
                                                                            mydata.append(temp_list)
                                                                            DOC_list.append(DOCID)
                                                                            DT_list.append(DATE)
                                                                            SLT_list.append(SLOT)
                                                                        print(tabulate(mydata, headers=head,
                                                                                       tablefmt="grid"))

                                                                        Return_Menu = input(
                                                                            "Please ENTER KEY to start booking an appointment")
                                                                        while n == 1:
                                                                            try:
                                                                                DOID = input(
                                                                                    "Enter Doctor ID: ").upper()
                                                                                if DOID in DOC_list:
                                                                                    print(
                                                                                        "Doctor ID exists, please proceed")
                                                                                    break
                                                                                else:
                                                                                    raise Exception
                                                                            except Exception:
                                                                                print(
                                                                                    "Doctor ID does not exists. Please recheck")
                                                                                print("")
                                                                        while n == 1:
                                                                            try:
                                                                                DateInput = str(
                                                                                    input('Enter date(yyyy-mm-dd): '))
                                                                                if DateInput in DT_list:
                                                                                    print(
                                                                                        "Dates are valid, please proceed")
                                                                                    print("")
                                                                                    break
                                                                                else:
                                                                                    raise Exception
                                                                            except Exception:
                                                                                print(
                                                                                    "Incorrect date format. Please recheck")
                                                                        while n == 1:
                                                                            try:
                                                                                EnterSlot = input(
                                                                                    "Select the slot number (Slot1, Slot2,..) ").upper()
                                                                                if EnterSlot in SLT_list:
                                                                                    cursor.execute(
                                                                                        "select DOC_ID,DATE,TIME_SLOT_START,DOC_NAME from DOCTOR_CALENDAR where DOC_ID = ? AND DATE = ? AND SLOT = ? ",
                                                                                        [DOID, DateInput, EnterSlot])
                                                                                    DTLS = cursor.fetchall()
                                                                                    for i in DTLS:
                                                                                        DOCTIDS = i[0]
                                                                                        DATETS = i[1]
                                                                                        STARTTIME = i[2]
                                                                                        DOCNAME = i[3]
                                                                                        cursor.execute(
                                                                                            "Update PatientData SET ScheduledAppointmentFlag = 1 WHERE PatientNumber = ? ",
                                                                                            [PatientNumber])
                                                                                        cursor.execute(
                                                                                            "UPDATE DOCTOR_CALENDAR SET PATIENT_NUMBER = ?, AVAILABLITY = 0 WHERE DOC_ID = ? AND DATE = ? AND SLOT = ? ",
                                                                                            [PatientNumber, DOCTIDS,
                                                                                             DATETS, EnterSlot])
                                                                                        cursor.execute(
                                                                                            "update PatientAppointment set DoctorName= ?, ScheduledDate= ?, ScheduledTime= ? where  PatientNumber = ? AND [AppointmentID] = ? ",
                                                                                            [DOCNAME, DATETS, STARTTIME,
                                                                                             PatientNumber, App_Input])
                                                                                        sqlConnection.commit()
                                                                                        print(
                                                                                            "Appointment Booked Successfully")
                                                                                        print("")
                                                                                        break
                                                                                    break
                                                                                else:
                                                                                    raise Exception
                                                                            except Exception:
                                                                                print(
                                                                                    "Incorrect input for slot, please enter valid slot id")
                                                        else:
                                                            print(
                                                                "There are no patients available to book appointments")
                                                            print("")
                                                            Return_Menu = input(
                                                                "Press ENTER KEY to go back to Main Menu")
                                                            break
                                                    except:
                                                        print(
                                                            "Invalid option. Please choose the options between 1 to 3")
                                                        print("")
                                                        Return_Menu = input("Press ENTER KEY to go back to Main Menu")
                                            elif staff_input == "3":
                                                while True:
                                                    try:
                                                        Cancel_Count = StaffDetails.Cancel_Count()
                                                        if Cancel_Count[0] >= 1:
                                                            print("There are " + str(Cancel_Count[
                                                                                         0]) + " patient(s) requested to cancel the appointment.")
                                                            Apnt_Cncl = StaffDetails.Cancel_Check()
                                                            APTD_List = {}
                                                            mydata = []
                                                            head = ["Appointment ID", "PATIENT NUMBER", "DOCTORNAME",
                                                                    "DATE", "STARTTIME"]
                                                            for Cancel in Apnt_Cncl:
                                                                APT_ID = Cancel[0]
                                                                PTNUM = Cancel[1]
                                                                DTRNM = Cancel[2]
                                                                SCDATE = Cancel[3]
                                                                SCTIME = Cancel[4]
                                                                temp_list = [APT_ID, PTNUM, DTRNM, SCDATE, SCTIME]
                                                                mydata.append(temp_list)
                                                                APTD_List[APT_ID] = {}
                                                                APTD_List[APT_ID]["PTNUM"] = PTNUM
                                                                APTD_List[APT_ID]["DTRNM"] = DTRNM
                                                                APTD_List[APT_ID]["SCDATE"] = SCDATE
                                                                APTD_List[APT_ID]["SCTIME"] = SCTIME
                                                            print(tabulate(mydata, headers=head, tablefmt="grid"))
                                                            Return_Menu = input(
                                                                "Please ENTER KEY to cancel the appointment")
                                                            while n == 1:
                                                                try:
                                                                    Can_Apt = int(input(
                                                                        "\nPlease enter the appointment ID to cancel the slot :"))
                                                                    if Can_Apt in APTD_List:
                                                                        DTR_NUM = APTD_List[Can_Apt]["DTRNM"]
                                                                        PT_NUM = APTD_List[Can_Apt]["PTNUM"]
                                                                        SC_DATE = APTD_List[Can_Apt]["SCDATE"]
                                                                        SC_TIME = APTD_List[Can_Apt]["SCTIME"]
                                                                        cursor.execute(
                                                                            "update DOCTOR_CALENDAR set PATIENT_NUMBER = '', AVAILABLITY = 1 WHERE DOC_ID = ? AND DATE = ? AND TIME_SLOT_START = ? ",
                                                                            [DTR_NUM, SC_DATE, SC_TIME])
                                                                        cursor.execute(
                                                                            "update PatientAppointment set Confirmedflag = 3 where PatientNumber = ? AND [AppointmentID] = ? ",
                                                                            [PT_NUM, Can_Apt])
                                                                        sqlConnection.commit()
                                                                        print("Appointment Cancelled Successfully")
                                                                        break
                                                                    else:
                                                                        raise Exception
                                                                except Exception:
                                                                    print("Invalid input, please enter valid input")
                                                                    Return_Menu = input(
                                                                        "Press ENTER KEY to go back to Main Menu")
                                                        else:
                                                            raise Exception
                                                    except Exception:
                                                        print(
                                                            "There are no patients requested for cancelling the appointments")
                                                        print("")
                                                        Return_Menu = input("Press ENTER KEY to go back to Main Menu")
                                                        break
                                            elif staff_input == "4":
                                                break
                                            else:
                                                print("Invalid option. Please choose the options between 1 to 4")
                                                print("")
                                                Return_Menu = input("Press ENTER KEY to go back to Main Menu")
                                    else:
                                        print("Incorrect password, please try again ")
                                        Password_Attempt = Password_Attempt + 1
                                        print("{} of {} attempts".format(Password_Attempt, Allow_Attempts))
                                        raise Exception
                                    break
                                except Exception:
                                    if Password_Attempt == 3:
                                        print("Attempts 3 of 3 completed for your password, please contact ADMIN")
                                        Password_Attempt = 0
                                        break

                        else:
                            raise Exception
                        break
                    except Exception:
                        print("")
                        print("Login ID does not exists, please contact ADMIN ")
                        break

            elif mod_input == 3:
                today = date.today()
                prescriptionDate = today.strftime("%Y-%m-%d")
                success = 'n'
                while success == 'n':
                    print(" ")
                    print("Please verify your Doctor Login")

                    username_SS = ""
                    password_SS = ""
                    username_SS = input("Enter your Doctor ID : ").upper()
                    password_SS = input("Enter your Password : ")
                    temp_d = ''
                    statement = "SELECT DOC_ID , PASSWORD,ACCESS_COUNT from DOCTOR_USERS WHERE DOC_ID='" + username_SS + "' AND PASSWORD = '" + password_SS + "'"
                    try:
                        cursor.execute(statement)
                        temp_d = cursor.fetchone()
                        accessCount = temp_d[2]
                        statement_two = "SELECT DOC_NAME FROM DOCTOR_DETAILS WHERE DOC_ID = '" + username_SS + "'"
                        cursor.execute(statement_two)
                        temp_name = cursor.fetchone()
                        doc_name = temp_name[0]
                        print(" ")
                        print("Welcome Dr." + doc_name)
                        success = 'y'
                    except Exception as e:
                        print("Invalid Login Details")
                        success = 'n'
                    else:
                        if accessCount == 0:
                            new_pass = input("\n Enter a new password of your choice:")
                            cursor.execute(
                                "UPDATE DOCTOR_USERS SET PASSWORD = '" + new_pass + "' WHERE DOC_ID = '" + username_SS + "'")
                            cursor.execute(
                                "UPDATE DOCTOR_USERS SET ACCESS_COUNT = '1' WHERE DOC_ID = '" + username_SS + "'")
                            cursor.execute("COMMIT")
                        print(" ")
                        success = 'y'
                while True:
                    try:
                        choice = 'Y'
                        while choice == 'Y':
                            print("\n Please pick your choice from below :")
                            print("\n Enter 1 to View Today's Appointments: ")
                            print("\n Enter 2 to View Prescriptions: ")
                            print("\n Enter 3 to View Doctor Calendar: ")
                            print("\n Enter N to Logout ")
                            print(" ")
                            option = input("\n Please enter your choice: ")
                            if option == '1':
                                print("---------------------Today's Appointments-----------------")
                                print(" ")
                                mydata = []
                                patientData = []
                                patientName = ''
                                patientNumber = ''
                                visited_status = ''
                                appointmentid = ''
                                allAppointments = []
                                statem = "SELECT PA.PatientNumber,PD.FirstName || ' ' ||  PD.LastName AS Name,PA.PrimarySymptoms || ',' || PA.OtherSymptoms AS Symptoms,PA.ScheduledDate, PA.AppointmentID ,PA.ScheduledTime FROM PatientAppointment PA JOIN PatientData PD on PD.PatientNumber = PA.PatientNumber WHERE PA.ScheduledDate='" + prescriptionDate + "' AND PA.DoctorName='" + doc_name + "' ORDER BY PA.ScheduledTime ";

                                for print_data_SS in cursor.execute(
                                        statem):
                                    patient_no = print_data_SS[0]
                                    date = print_data_SS[3]
                                    name = print_data_SS[1]
                                    symptom = print_data_SS[2]
                                    allAppointments.append(print_data_SS[4])

                                    temp_list = [print_data_SS[4], date, print_data_SS[5], patient_no, name,
                                                 symptom]
                                    mydata.append(temp_list)

                                head = ["APPOINTMENT NUMBER", "DATE", "TIME", "PATIENT N0.", "PATIENT NAME",
                                        "SYMPTOMS"]
                                if len(allAppointments)==0:
                                    print("Sorry!There are no appointments for today")
                                else:
                                    print(tabulate(mydata, headers=head, tablefmt="grid"))
                                    print(" ")
                                    apFlag = 0
                                    patient_no = input("Enter an Appointment number to View Details: ")

                                    while apFlag == 0:
                                        try:
                                            if int(patient_no) not in allAppointments:
                                                print("Invalid Appointment number")
                                                patient_no = input("Enter a Appointment number to View Details: ")
                                            else:
                                                apFlag = 1
                                        except:
                                            print("Invalid Appointment Number")
                                            patient_no = input("Enter a Appointment number to View Details: ")
                                    appid = ''
                                    for print_data_SS in cursor.execute(
                                            "SELECT PD.PatientID,PD.PatientNumber, PD.FirstName || ' ' || PD.LastName AS NAME,PA.PrimarySymptoms,PA.OtherSymptoms,PA.AppointmentID AS appid FROM PatientData PD JOIN PatientAppointment PA ON PA.PatientNumber = PD.PatientNumber WHERE PA.AppointmentID='" + patient_no + "'"):
                                        patientNumber = print_data_SS[1]
                                        fullName = print_data_SS[2]
                                        patientName = fullName
                                        appid = print_data_SS[5]
                                        temp_patient_data = [appid, print_data_SS[1], fullName, print_data_SS[3],
                                                             print_data_SS[4]]
                                        patientData.append(temp_patient_data)
                                    head = ["APPOINTMENT ID", "PATIENT NUMBER", "NAME", "PRIMARY SYMPTOM",
                                            "OTHER SYMPTOM"]
                                    print(tabulate(patientData, headers=head, tablefmt="grid"))

                                    prescription = input("Add a Prescription for " + patientName + " :")

                                    cursor.execute(
                                        "INSERT INTO prescription (PatientNumber, prescription, prescription_date,DoctorId,AppointmentID) VALUES('" + str(
                                            patientNumber) + "','" + str(prescription) + "', '" + str(
                                            prescriptionDate) + "', '" + str(username_SS) + "', '" + str(
                                            appid) + "')");
                                    cursor.execute("COMMIT");
                                    print(" ")
                                    print("The Prescription has been Added")
                                    print(" ")
                                    choice = input("Enter Y to view Menu or N to Logout: ")
                                    choice = choice.upper()
                            if option == '2':
                                mydata = []
                                patientData = []
                                patientName = ''
                                patientNumber = ''
                                visited_status = ''
                                appointmentid = ''
                                allAppointments = []
                                statem = "SELECT PA.PatientNumber,PD.FirstName || ' ' ||  PD.LastName AS Name,PA.PrimarySymptoms || ',' || PA.OtherSymptoms AS Symptoms,PA.ScheduledDate, PA.AppointmentID ,PA.ScheduledTime FROM PatientAppointment PA JOIN PatientData PD on PD.PatientNumber = PA.PatientNumber WHERE PA.ScheduledDate='" + prescriptionDate + "' AND PA.DoctorName='" + doc_name + "' ORDER BY PA.ScheduledTime ";
                                # print(statem)
                                for print_data_SS in cursor.execute(
                                        statem):
                                    patient_no = print_data_SS[0]
                                    date = print_data_SS[3]
                                    name = print_data_SS[1]
                                    symptom = print_data_SS[2]
                                    allAppointments.append(print_data_SS[0])

                                    temp_list = [print_data_SS[4], date, print_data_SS[5], patient_no, name,
                                                 symptom]
                                    mydata.append(temp_list)

                                head = ["APPOINTMENT NUMBER", "DATE", "TIME", "PATIENT N0.", "PATIENT NAME",
                                        "SYMPTOMS"]
                                if len(allAppointments)==0:
                                    print("Sorry!There are no appointments for today")
                                else:
                                    print(tabulate(mydata, headers=head, tablefmt="grid"))
                                    print(" ")
                                    apFlag = 0
                                    patient_no = input("Enter a Patient number to View Prescriptions: ")
                                    patientsData = []
                                    while apFlag == 0:
                                        try:
                                            if int(patient_no) not in allAppointments:
                                                print("Invalid Patient number")
                                                patient_no = input("Enter a Patient number to View Details: ")
                                            else:
                                                apFlag = 1
                                        except:
                                            print("Invalid Patient Number")
                                            patient_no = input("Enter a Patient number to View Details: ")
                                    for print_data_SS in cursor.execute(
                                            "SELECT AppointmentID,PatientNumber,DoctorId,prescription,prescription_date FROM prescription P WHERE P.PatientNumber = '" + patient_no + "'"):
                                        temp_pat_data = [print_data_SS[0], print_data_SS[1], print_data_SS[2],
                                                         print_data_SS[3], print_data_SS[4]]
                                        patientData.append(temp_pat_data)
                                    head = ["APPOINTMENT NUMBER", "PATIENT NUMBER", "DOCTOR ID", "PRESCRIPTION",
                                            "PRESCRIPTION DATE"]
                                    print(tabulate(patientData, headers=head, tablefmt="grid"))
                                    choice = input("Enter Y to view Menu or N to Logout: ")
                                    choice = choice.upper()

                            if option == '3':
                                calendarData = []
                                print(" ")
                                print("---------------------------------MY CALENDAR-------------------------------")
                                statement = "SELECT DATE,SHIFT_TYPE,TIME_SLOT_START,PATIENT_NUMBER FROM DOCTOR_CALENDAR DC WHERE DC.DOC_ID = '"+username_SS+"'";
                                for print_data_SS in cursor.execute(statement):
                                    temp_cal_data = [print_data_SS[0],print_data_SS[1],print_data_SS[2], print_data_SS[3]]
                                    calendarData.append(temp_cal_data)
                                head = ["DATE", "SHIFT TYPE", "TIME SLOT", "PATIENT N0."]
                                print(tabulate(calendarData, headers=head, tablefmt="grid"))
                                choice = input("Enter Y to view Menu or N to Logout: ")
                                choice=choice.upper()
                            if option == 'N' or option=='n':
                                break





                        break
                    except Exception as e:

                        print("")
                        Return_Menu = input("Press ENTER KEY to go back to Main Menu")
                        break

            elif mod_input == 4:
                print("############################################")
                print("############################################")
                print("Welcome to the ADMIN LOGIN SYSTEM")
                print("############################################")
                print("############################################")
                admin_main = AdminModule()
                admin_main.admin_user_login(admin_main)
            elif mod_input == 5:
                print("Exiting..... Good Bye!!")
                break
            

        except:
            print("Invalid option. Please choose the options between 1 to 4")
            print("")
            Return_Menu = input("Press ENTER KEY to go back to Main Menu")
